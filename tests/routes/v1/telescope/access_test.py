from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.security import SecurityScopes

from across_server.auth.schemas import AuthUser
from across_server.routes.v1.telescope.access import TelescopeAccess, telescope_access
from across_server.routes.v1.telescope.exceptions import TelescopeNotFoundException


@pytest.fixture()
def mock_group_access(
    fake_auth_user: AuthUser,
) -> Generator[MagicMock, None, None]:
    with patch("across_server.routes.v1.telescope.access.group_access") as m:
        m.return_value = fake_auth_user
        yield m


class TestTelescopeAccess:
    @pytest.mark.asyncio
    async def test_should_return_auth_user_when_telescope_found(
        self,
        mock_group_access: MagicMock,
        mock_db: AsyncMock,
        mock_result: MagicMock,
        fake_auth_user: AuthUser,
    ) -> None:
        """Should return auth_user when telescope is found and group_access succeeds"""
        mock_result.scalar_one_or_none.return_value = uuid4()

        result = await telescope_access(
            security_scopes=SecurityScopes([]),
            auth_user=fake_auth_user,
            db=mock_db,
            data=TelescopeAccess(telescope_id=uuid4()),
        )

        assert result == fake_auth_user

    @pytest.mark.asyncio
    async def test_should_raise_telescope_not_found_when_telescope_missing(
        self,
        mock_group_access: MagicMock,
        mock_db: AsyncMock,
        mock_result: MagicMock,
        fake_auth_user: AuthUser,
    ) -> None:
        """Should raise TelescopeNotFoundException when telescope is not found"""
        mock_result.scalar_one_or_none.return_value = None

        with pytest.raises(TelescopeNotFoundException):
            await telescope_access(
                security_scopes=SecurityScopes([]),
                auth_user=fake_auth_user,
                db=mock_db,
                data=TelescopeAccess(telescope_id=uuid4()),
            )

    @pytest.mark.asyncio
    async def test_should_call_group_access(
        self,
        mock_group_access: MagicMock,
        mock_db: AsyncMock,
        mock_result: MagicMock,
        fake_auth_user: AuthUser,
    ) -> None:
        """Should call group_access"""
        group_id = uuid4()
        mock_result.scalar_one_or_none.return_value = group_id

        await telescope_access(
            security_scopes=SecurityScopes([]),
            auth_user=fake_auth_user,
            db=mock_db,
            data=TelescopeAccess(telescope_id=uuid4()),
        )

        mock_group_access.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_pass_group_id_to_group_access(
        self,
        mock_group_access: MagicMock,
        mock_db: AsyncMock,
        mock_result: MagicMock,
        fake_auth_user: AuthUser,
    ) -> None:
        """Should pass the resolved group_id to group_access"""
        group_id = uuid4()
        mock_result.scalar_one_or_none.return_value = group_id

        await telescope_access(
            security_scopes=SecurityScopes([]),
            auth_user=fake_auth_user,
            db=mock_db,
            data=TelescopeAccess(telescope_id=uuid4()),
        )

        assert mock_group_access.call_args[1]["group_id"] == group_id
