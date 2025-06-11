from typing import Annotated, TypedDict
from uuid import UUID

import argon2
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..auth.hashing import password_hasher
from ..core.exceptions import AcrossHTTPException
from ..db import get_session, models
from . import magic_link, schemas, tokens
from .config import auth_config


class Tokens(TypedDict):
    access: str
    refresh: str


class AuthService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    def generate_magic_link(self, email: str) -> str:
        return magic_link.generate(email)

    async def authenticate_user(
        self,
        token: str,
    ) -> schemas.AuthUser:
        token_data = tokens.AccessToken().decode(token)
        auth_user = await self.get_authenticated_user(user_id=UUID(token_data.sub))

        return auth_user

    async def authenticate_service_account(
        self, credentials: HTTPBasicCredentials
    ) -> schemas.AuthUser:
        query = select(models.ServiceAccount).where(
            (models.ServiceAccount.id == credentials.username)
        )

        result = await self.db.execute(query)
        service_account = result.unique().scalar_one_or_none()

        if service_account is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        # !!! COMPARE PASSWORD HERE USING ARGON2 !!!
        try:
            password_hasher.verify(
                service_account.hashed_key,
                credentials.password + auth_config.SERVICE_ACCOUNT_SECRET_KEY,
            )
            auth_user = await self.get_authenticated_service_account(
                username=UUID(credentials.username)
            )
            return auth_user
        except (
            argon2.exceptions.VerifyMismatchError,
            argon2.exceptions.VerificationError,
            argon2.exceptions.InvalidHashError,
        ):
            raise AcrossHTTPException(
                400,
                "invalid_grant",
                {"reason": f"invalid password for user [{credentials.username}]"},
            )

    async def authenticate_jwt(
        self,
        token: str,
    ) -> schemas.AuthUser:
        token_data = tokens.AccessToken().decode(token)

        if token_data.type == "user":
            auth_user = await self.get_authenticated_user(user_id=UUID(token_data.sub))
        elif token_data.type == "service_account":
            auth_user = await self.get_authenticated_service_account(
                username=UUID(token_data.sub)
            )

        return auth_user

    def get_auth_tokens(
        self,
        auth_user: schemas.AuthUser,
    ) -> Tokens:
        access_token = tokens.AccessToken()
        refresh_token = tokens.RefreshToken()

        encoded_access_token = access_token.encode(access_token.to_encode(auth_user))
        encoded_refresh_token = refresh_token.encode(
            refresh_token.to_encode(auth_user.id)
        )

        return Tokens(access=encoded_access_token, refresh=encoded_refresh_token)

    async def get_authenticated_user(
        self,
        user_id: UUID | None = None,
        email: EmailStr | None = None,
    ) -> schemas.AuthUser:
        query = (
            select(models.User)
            .where((models.User.id == user_id) | (models.User.email == email))
            .options(joinedload(models.User.roles).joinedload(models.Role.permissions))
            .options(
                joinedload(models.User.groups)
                .joinedload(models.Group.roles)
                .joinedload(models.GroupRole.permissions)
            )
        )

        result = await self.db.execute(query)
        user = result.unique().scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        # Extract unique permissions into a set and convert to a list
        unique_permissions = list(
            {perm.name for role in user.roles for perm in role.permissions}
        )

        auth_user = schemas.AuthUser(
            id=user.id,
            groups=[],
            scopes=unique_permissions,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            type=schemas.AuthUserType.USER,
        )

        if user.groups:
            for group in user.groups:
                unique_group_perms = list(
                    {
                        perm.name
                        for role in (group.roles or [])
                        for perm in role.permissions
                    }
                )

                auth_user.groups.append(
                    schemas.Group(id=group.id, scopes=unique_group_perms)
                )

        return auth_user

    async def get_authenticated_service_account(
        self,
        username: UUID,
    ) -> schemas.AuthUser:
        query = (
            select(models.ServiceAccount)
            .where((models.ServiceAccount.id == username))
            .options(
                joinedload(models.ServiceAccount.group_roles).joinedload(
                    models.GroupRole.permissions
                )
            )
            .options(joinedload(models.ServiceAccount.user))
        )

        result = await self.db.execute(query)
        service_account = result.unique().scalar_one_or_none()

        if service_account is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        groups = []
        # Extract group_ids from group_roles into a deduplicated set
        group_ids = set(
            {group_role.group.id for group_role in service_account.group_roles}
        )
        for id in group_ids:
            groups.append(
                schemas.Group(
                    id=id,
                    # aggregate all permissions for a group_id
                    scopes=[
                        perm.name
                        for group_role in service_account.group_roles
                        for perm in group_role.permissions
                        if group_role.group.id == id
                    ],
                )
            )

        auth_user = schemas.AuthUser(
            id=service_account.id,
            groups=groups,
            scopes=[],
            first_name=service_account.user.first_name,
            last_name=service_account.user.last_name,
            username=service_account.user.username,
            type=schemas.AuthUserType.SERVICE_ACCOUNT,
        )

        return auth_user
