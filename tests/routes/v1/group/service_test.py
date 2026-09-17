import uuid
from unittest.mock import AsyncMock, patch

import pytest

from across_server.db import models
from across_server.routes.v1.group.exceptions import GroupNotFoundException
from across_server.routes.v1.group.role.service import GroupRoleService
from across_server.routes.v1.group.service import GroupService


class TestGroupService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_raise_group_not_found_when_group_is_none(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            mock_result.unique.return_value.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)
            with pytest.raises(GroupNotFoundException):
                await group_service.get(uuid.uuid4())

        @pytest.mark.asyncio
        async def test_should_return_instance_of_group(
            self, mock_db: AsyncMock, mock_result: AsyncMock, fake_group: models.Group
        ) -> None:
            mock_result.unique.return_value.scalar_one_or_none.return_value = fake_group
            mock_db.execute.return_value = mock_result
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)

            group = await group_service.get(uuid.uuid4())
            assert isinstance(group, models.Group)

    class TestRemoveUser:
        @pytest.mark.asyncio
        async def test_remove_user_should_remove_group_roles_from_user(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_user: models.User,
            fake_group_role: models.GroupRole,
        ) -> None:
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)

            with patch.object(group_service, "get", return_value=fake_group):
                await group_service.remove_user(fake_user, fake_group.id)
                assert fake_group_role not in fake_user.group_roles

        @pytest.mark.asyncio
        async def test_remove_user_should_remove_group_roles_from_user_service_account(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_user: models.User,
            fake_group_role: models.GroupRole,
        ) -> None:
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)

            with patch.object(group_service, "get", return_value=fake_group):
                await group_service.remove_user(fake_user, fake_group.id)
                assert fake_group_role not in fake_user.service_accounts[0].group_roles

        @pytest.mark.asyncio
        async def test_remove_user_should_remove_user_from_group(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_user: models.User,
        ) -> None:
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)

            with patch.object(group_service, "get", return_value=fake_group):
                await group_service.remove_user(fake_user, fake_group.id)
                assert fake_user not in fake_group.users
