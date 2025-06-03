import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from across_server.auth import schemas
from across_server.auth.service import AuthService
from across_server.db.models import User


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
        assert link.__contains__("/auth/verify?token=mock_token")

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
            mock_user_data: User,
        ) -> None:
            mock_scalar_one_or_none.return_value = mock_user_data
            service = AuthService(mock_db)
            authUser = await service.get_authenticated_user(
                uuid.uuid4(), "testEmail@example.com"
            )
            assert isinstance(authUser, schemas.AuthUser)
            assert authUser.type == "user"

        @pytest.mark.asyncio
        async def test_get_authenticated_user_should_return_type_user(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            mock_user_data: User,
        ) -> None:
            mock_scalar_one_or_none.return_value = mock_user_data
            service = AuthService(mock_db)
            authUser = await service.get_authenticated_user(
                uuid.uuid4(), "testEmail@example.com"
            )
            assert authUser.type == "user"

    class TestGetAuthenticatedServiceAccount:
        @pytest.mark.asyncio
        async def test_get_authenticated_service_account_should_return_auth_user(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            mock_service_account_data: User,
        ) -> None:
            mock_scalar_one_or_none.return_value = mock_service_account_data
            service = AuthService(mock_db)
            authUser = await service.get_authenticated_service_account(uuid.uuid4())
            assert isinstance(authUser, schemas.AuthUser)

        @pytest.mark.asyncio
        async def test_get_authenticated_service_account_should_return_type_service_account(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            mock_service_account_data: User,
        ) -> None:
            mock_scalar_one_or_none.return_value = mock_service_account_data
            service = AuthService(mock_db)
            authUser = await service.get_authenticated_service_account(uuid.uuid4())
            assert authUser.type == "service_account"
