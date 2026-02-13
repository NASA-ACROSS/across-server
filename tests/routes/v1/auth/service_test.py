import datetime
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from across_server.auth import schemas
from across_server.auth.service import AuthService
from across_server.core.exceptions import AcrossHTTPException
from across_server.db.models import Group, GroupRole, ServiceAccount, User


class TestAuthService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.email = "mockemail"

    def test_generate_magic_link_returns_link(
        self,
        mock_db: AsyncMock,
    ) -> None:
        """Should return a new link when calling generate_magic_link"""
        service = AuthService(mock_db)
        link = service.generate_magic_link(self.email)
        assert link.__contains__("login-verify?token=mock_token")

    def test_should_throw_error_when_magic_link_generation_fails(
        self, mock_db: AsyncMock, mock_magic_link_generate: MagicMock
    ) -> None:
        """Should throw an error when calling generate_magic_link fails"""
        mock_magic_link_generate.side_effect = Exception("Mock Exception")
        with pytest.raises(Exception):
            service = AuthService(mock_db)
            service.generate_magic_link(self.email)

    class TestGetAuthenticatedUser:
        @pytest.mark.asyncio
        async def test_get_authenticated_user_should_return_auth_user(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_user: User,
        ) -> None:
            mock_scalar_one_or_none.return_value = fake_user
            service = AuthService(mock_db)
            auth_user = await service.get_authenticated_user(
                uuid.uuid4(), "testEmail@example.com"
            )
            assert isinstance(auth_user, schemas.AuthUser)

        @pytest.mark.asyncio
        async def test_get_authenticated_user_should_return_type_user(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_user: User,
        ) -> None:
            mock_scalar_one_or_none.return_value = fake_user
            service = AuthService(mock_db)
            auth_user = await service.get_authenticated_user(
                uuid.uuid4(), "testEmail@example.com"
            )
            assert auth_user.type == schemas.PrincipalType.USER

        @pytest.mark.asyncio
        async def test_get_authenticated_user_should_throw_when_user_is_deleted_and_not_found(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
        ) -> None:
            mock_scalar_one_or_none.return_value = None
            service = AuthService(mock_db)

            with pytest.raises(HTTPException):
                await service.get_authenticated_user(
                    uuid.uuid4(), "testEmail@example.com"
                )

    class TestGetAuthenticatedServiceAccount:
        @pytest.mark.asyncio
        async def test_get_authenticated_service_account_should_return_auth_user(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_service_account: User,
            fake_group_role: GroupRole,
            fake_group: Group,
        ) -> None:
            mock_scalar_one_or_none.return_value = fake_service_account
            fake_group_role.group = fake_group
            service = AuthService(mock_db)
            auth_user = await service.get_authenticated_service_account(uuid.uuid4())
            assert isinstance(auth_user, schemas.AuthUser)

        @pytest.mark.asyncio
        async def test_get_authenticated_service_account_should_return_type_service_account(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_service_account: User,
            fake_group_role: GroupRole,
            fake_group: Group,
        ) -> None:
            mock_scalar_one_or_none.return_value = fake_service_account
            fake_group_role.group = fake_group
            service = AuthService(mock_db)
            authUser = await service.get_authenticated_service_account(uuid.uuid4())
            assert authUser.type == schemas.PrincipalType.SERVICE_ACCOUNT

        @pytest.mark.asyncio
        async def test_get_authenticated_service_account_should_throw_when_owner_is_deleted(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_service_account: ServiceAccount,
            fake_user: User,
        ) -> None:
            fake_user.is_deleted = True
            fake_service_account.user = [fake_user]
            mock_scalar_one_or_none.return_value = fake_service_account
            service = AuthService(mock_db)
            with pytest.raises(HTTPException):
                await service.get_authenticated_service_account(uuid.uuid4())

        @pytest.mark.asyncio
        async def test_get_authenticated_service_account_should_return_system_service_account_when_no_owner(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_user: User,
            fake_group: Group,
        ) -> None:
            # test setup using existing mocks to prevent circular imports in conftest
            fake_service_account = fake_user.service_accounts[0]
            fake_service_account.group_roles[0].group_id = (
                fake_group.users[0].groups[0].id
            )
            del fake_service_account.user
            mock_scalar_one_or_none.return_value = fake_service_account

            service = AuthService(mock_db)
            authUser = await service.get_authenticated_service_account(
                fake_service_account.id
            )
            assert authUser.type == schemas.PrincipalType.SERVICE_ACCOUNT

    class TestAuthenticateServiceAccount:
        @pytest.mark.asyncio
        async def test_authenticate_service_account_should_throw_when_password_mismatch(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_service_account: ServiceAccount,
        ) -> None:
            mock_scalar_one_or_none.return_value = fake_service_account
            service = AuthService(mock_db)

            with pytest.raises(AcrossHTTPException):
                await service.authenticate_service_account(
                    HTTPBasicCredentials(
                        username=str(fake_service_account.id),
                        password="WRONG!PASSWORD",
                    )
                )

        @pytest.mark.asyncio
        async def test_authenticate_service_account_should_return_auth_user_when_password_match(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_service_account: User,
            fake_group: Group,
            fake_group_role: GroupRole,
        ) -> None:
            mock_scalar_one_or_none.return_value = fake_service_account
            fake_group_role.group = fake_group
            service = AuthService(mock_db)
            auth_user = await service.authenticate_service_account(
                HTTPBasicCredentials(
                    username=str(fake_service_account.id), password="PASSWORD"
                )
            )
            assert isinstance(auth_user, schemas.AuthUser)

        @pytest.mark.asyncio
        async def test_authenticate_service_account_should_throw_when_expired(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_service_account: ServiceAccount,
            fake_time: datetime.datetime,
        ) -> None:
            fake_service_account.expiration = fake_time - datetime.timedelta(days=10)
            mock_scalar_one_or_none.return_value = fake_service_account
            service = AuthService(mock_db)

            with pytest.raises(HTTPException):
                await service.authenticate_service_account(
                    HTTPBasicCredentials(
                        username=str(fake_service_account.id),
                        password="PASSWORD",
                    )
                )
