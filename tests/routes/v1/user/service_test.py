from unittest.mock import AsyncMock

import pytest

from across_server.db import models
from across_server.routes.v1.user.exceptions import UserEmailNotFoundException
from across_server.routes.v1.user.service import UserService


class TestUserService:
    class TestGetByEmail:
        @pytest.mark.asyncio
        async def test_should_return_user_if_email_exists(
            self,
            mock_db: AsyncMock,
            mock_scalar_result: AsyncMock,
            mock_user_data: models.User,
        ) -> None:
            mock_scalar_result.one_or_none.return_value = mock_user_data
            service = UserService(mock_db)
            user = await service.get_by_email("sandy@treedome.space")
            assert isinstance(user, models.User)

        @pytest.mark.asyncio
        async def test_should_raise_user_email_not_found_error_when_user_is_none(
            self,
            mock_db: AsyncMock,
            mock_scalar_result: AsyncMock,
            mock_user_data: models.User,
        ) -> None:
            mock_scalar_result.one_or_none.return_value = None
            service = UserService(mock_db)
            with pytest.raises(UserEmailNotFoundException):
                await service.get_by_email("sandy@treedome.space")
