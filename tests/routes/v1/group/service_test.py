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
        async def test_get_should_raise_group_not_found_when_group_is_none(
            self, mock_db: AsyncMock
        ) -> None:
            mock_db.get.return_value = None
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)
            with pytest.raises(GroupNotFoundException):
                await group_service.get(uuid.uuid4())

        @pytest.mark.asyncio
        async def test_get_should_return_instance_of_group(
            self, mock_db: AsyncMock, mock_group_data: models.Group
        ) -> None:
            mock_db.get.return_value = mock_group_data
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)

            group = await group_service.get(uuid.uuid4())
            assert isinstance(group, models.Group)

    class TestRemoveUser:
        @pytest.mark.asyncio
        async def test_remove_user_should_remove_group_roles_from_user(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_user_data: models.User,
            mock_group_role_data: models.GroupRole,
        ) -> None:
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)

            with patch.object(group_service, "get", return_value=mock_group_data):
                await group_service.remove_user(mock_user_data, mock_group_data.id)
                assert mock_group_role_data not in mock_user_data.group_roles

        @pytest.mark.asyncio
        async def test_remove_user_should_remove_group_roles_from_user_service_account(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_user_data: models.User,
            mock_group_role_data: models.GroupRole,
        ) -> None:
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)

            with patch.object(group_service, "get", return_value=mock_group_data):
                await group_service.remove_user(mock_user_data, mock_group_data.id)
                assert (
                    mock_group_role_data
                    not in mock_user_data.service_accounts[0].group_roles
                )

        @pytest.mark.asyncio
        async def test_remove_user_should_remove_user_from_group(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_user_data: models.User,
        ) -> None:
            group_role_service = GroupRoleService(mock_db)
            group_service = GroupService(mock_db, group_role_service)

            with patch.object(group_service, "get", return_value=mock_group_data):
                await group_service.remove_user(mock_user_data, mock_group_data.id)
                assert mock_user_data not in mock_group_data.users
