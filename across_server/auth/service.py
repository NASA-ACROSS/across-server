from typing import Annotated, TypedDict
from uuid import UUID

from fastapi import Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..db import get_session, models
from . import magic_link, schemas, tokens


class Tokens(TypedDict):
    access: str
    refresh: str


class AuthService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]):
        self.db = db

    def generate_magic_link(self, email: str) -> str:
        return magic_link.generate(email)

    async def authenticate(
        self,
        token: str,
    ):
        token_data = tokens.AccessToken().decode(token)
        auth_user = await self.get_authenticated_user(user_id=UUID(token_data.sub))

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
                    schemas.Group(id=str(group.id), scopes=unique_group_perms)
                )

        return auth_user
