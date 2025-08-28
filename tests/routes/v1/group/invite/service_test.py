import uuid
from unittest.mock import AsyncMock, patch

import pytest

from across_server.core.exceptions import DuplicateEntityException
from across_server.db import models
from across_server.routes.v1.group.invite.exceptions import GroupInviteNotFoundException
from across_server.routes.v1.group.invite.service import GroupInviteService


class TestGroupInviteService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_group_invite_when_successful(
            self,
            mock_db: AsyncMock,
            mock_scalar_result: AsyncMock,
            fake_group_invite: models.GroupInvite,
        ) -> None:
            """Should return a GroupInvite model when get is successful"""
            mock_scalar_result.one_or_none.return_value = fake_group_invite
            service = GroupInviteService(mock_db)

            user_invite = await service.get(uuid.uuid4(), uuid.uuid4())

            assert isinstance(user_invite, models.GroupInvite)

        @pytest.mark.asyncio
        async def test_should_throw_exception_when_invite_not_found(
            self, mock_db: AsyncMock, mock_scalar_result: AsyncMock
        ) -> None:
            """Should throw exception when user invite not found"""
            mock_scalar_result.one_or_none.return_value = None
            service = GroupInviteService(mock_db)

            with pytest.raises(GroupInviteNotFoundException):
                await service.get(uuid.uuid4(), uuid.uuid4())

    class TestGetMany:
        @pytest.mark.asyncio
        async def test_should_return_list_when_successful(
            self,
            mock_db: AsyncMock,
            mock_scalar_result: AsyncMock,
            fake_group_invite: models.GroupInvite,
        ) -> None:
            """Should return an list of GroupInvite models when get_many is successful"""
            mock_scalar_result.all.return_value = [
                fake_group_invite,
                fake_group_invite,
            ]
            service = GroupInviteService(mock_db)

            user_invites = await service.get_many(
                uuid.uuid4(),
            )

            assert isinstance(user_invites, list)

        @pytest.mark.asyncio
        async def test_should_return_list_of_group_invites_when_successful(
            self,
            mock_db: AsyncMock,
            mock_scalar_result: AsyncMock,
            fake_group_invite: models.GroupInvite,
        ) -> None:
            """Should return an list of GroupInvite models when get_many is successful"""
            mock_scalar_result.all.return_value = [
                fake_group_invite,
                fake_group_invite,
            ]
            service = GroupInviteService(mock_db)

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
            """Should return an list of GroupInvite models when get_many is successful"""
            mock_scalar_result.all.return_value = []
            service = GroupInviteService(mock_db)

            user_invites = await service.get_many(
                uuid.uuid4(),
            )

            assert isinstance(user_invites, list)

    class TestSend:
        @pytest.mark.asyncio
        async def test_should_raise_duplicate_entity_exception_when_user_in_group(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_user: models.User,
        ) -> None:
            service = GroupInviteService(mock_db)

            fake_group.users = [fake_user]

            with pytest.raises(DuplicateEntityException):
                await service.send(uuid.uuid4(), fake_group, fake_user)

        @pytest.mark.asyncio
        async def test_should_raise_duplicate_entity_exception_when_user_already_invited(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_user: models.User,
            fake_group_invite: models.GroupInvite,
        ) -> None:
            service = GroupInviteService(mock_db)

            with patch.object(service, "get_many", return_value=[fake_group_invite]):
                with pytest.raises(DuplicateEntityException):
                    await service.send(uuid.uuid4(), fake_group, fake_user)

        @pytest.mark.asyncio
        async def test_should_return_instance_of_group_invite_when_successful(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_user: models.User,
        ) -> None:
            service = GroupInviteService(mock_db)

            # assume no users are in the group
            fake_group.users = []

            with patch.object(service, "get_many", return_value=[]):
                invite = await service.send(uuid.uuid4(), fake_group, fake_user)
                assert isinstance(invite, models.GroupInvite)

        @pytest.mark.asyncio
        async def test_should_add_group_invite_to_database_when_successful(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_user: models.User,
        ) -> None:
            service = GroupInviteService(mock_db)

            fake_group.users = []

            with patch.object(service, "get_many", return_value=[]):
                invite = await service.send(uuid.uuid4(), fake_group, fake_user)
                mock_db.add.assert_called_once_with(invite)

    class TestAccept:
        @pytest.mark.asyncio
        async def test_should_append_user_to_group(
            self, mock_db: AsyncMock, fake_group_invite: models.GroupInvite
        ) -> None:
            service = GroupInviteService(mock_db)

            await service.accept(fake_group_invite)
            assert fake_group_invite.receiver in fake_group_invite.group.users

        @pytest.mark.asyncio
        async def test_should_call_db_delete_with_invite_record_once_when_successful(
            self, mock_db: AsyncMock, fake_group_invite: models.GroupInvite
        ) -> None:
            service = GroupInviteService(mock_db)

            await service.accept(fake_group_invite)
            mock_db.delete.assert_called_once_with(fake_group_invite)

    class TestDelete:
        @pytest.mark.asyncio
        async def test_should_call_db_delete_with_invite_record_once_when_successful(
            self, mock_db: AsyncMock, fake_group_invite: models.GroupInvite
        ) -> None:
            service = GroupInviteService(mock_db)

            await service.delete(fake_group_invite)
            mock_db.delete.assert_called_once_with(fake_group_invite)
