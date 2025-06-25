import uuid
from unittest.mock import AsyncMock

import pytest

from across_server.db import models
from across_server.routes.v1.group.invite.exceptions import GroupInviteNotFoundException
from across_server.routes.v1.user.invite.service import UserInviteService


class TestUserInviteService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_group_invite_when_successful(
            self,
            mock_db: AsyncMock,
            mock_scalar_result: AsyncMock,
            mock_group_invite_data: models.GroupInvite,
        ) -> None:
            """Should return a single GroupInvite model when get is successful"""
            mock_scalar_result.one_or_none.return_value = mock_group_invite_data
            service = UserInviteService(mock_db)

            user_invite = await service.get(uuid.uuid4(), uuid.uuid4())

            assert isinstance(user_invite, models.GroupInvite)

        @pytest.mark.asyncio
        async def test_should_throw_exception_when_invite_not_found(
            self, mock_db: AsyncMock, mock_scalar_result: AsyncMock
        ) -> None:
            """Should throw exception when user invite not found"""
            mock_scalar_result.one_or_none.return_value = None
            service = UserInviteService(mock_db)

            with pytest.raises(GroupInviteNotFoundException):
                await service.get(uuid.uuid4(), uuid.uuid4())

    class TestGetMany:
        @pytest.mark.asyncio
        async def test_should_return_list_when_successful(
            self,
            mock_db: AsyncMock,
            mock_scalar_result: AsyncMock,
            mock_group_invite_data: models.GroupInvite,
        ) -> None:
            """Should return an list of GroupInvite models when get_many is successful"""
            mock_scalar_result.all.return_value = [
                mock_group_invite_data,
                mock_group_invite_data,
            ]
            service = UserInviteService(mock_db)

            user_invites = await service.get_many(
                uuid.uuid4(),
            )

            assert isinstance(user_invites, list)

        @pytest.mark.asyncio
        async def test_should_return_list_of_group_invites_when_successful(
            self,
            mock_db: AsyncMock,
            mock_scalar_result: AsyncMock,
            mock_group_invite_data: models.GroupInvite,
        ) -> None:
            """Should return a list of GroupInvite models when get_many is successful"""
            mock_scalar_result.all.return_value = [
                mock_group_invite_data,
                mock_group_invite_data,
            ]
            service = UserInviteService(mock_db)

            user_invites = await service.get_many(
                uuid.uuid4(),
            )

            for user_invite in user_invites:
                assert isinstance(user_invite, models.GroupInvite)

        @pytest.mark.asyncio
        async def test_should_return_empty_list_when_successful(
            self,
            mock_db: AsyncMock,
            mock_scalar_result: AsyncMock,
        ) -> None:
            """Should return an empty list when no invites for user"""
            mock_scalar_result.all.return_value = []
            service = UserInviteService(mock_db)

            user_invites = await service.get_many(
                uuid.uuid4(),
            )

            assert isinstance(user_invites, list)
