import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.db import models
from across_server.routes.group.exceptions import GroupNotFoundException
from across_server.routes.group.role.exceptions import GroupRoleNotFoundException
from across_server.routes.group.role.service import (
    GroupRoleService,
)


class TestGroupRoleService:
    class TestAssign:
        @pytest.mark.asyncio
        async def test_should_return_group_role_when_successful(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_group_role_data: models.GroupRole,
            mock_user_data: models.User,
        ) -> None:
            """Should return the group role when assign is successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.assign(
                mock_group_role_data,
                mock_user_data,
                mock_group_data,
            )
            assert isinstance(group_role, models.GroupRole)

        @pytest.mark.asyncio
        async def test_should_add_group_role_to_user_when_successful(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_group_role_data: models.GroupRole,
            mock_user_data: models.User,
        ) -> None:
            """Should add group role to user when successful"""
            mock_user_data.group_roles = []

            service = GroupRoleService(mock_db)
            await service.assign(
                mock_group_role_data,
                mock_user_data,
                mock_group_data,
            )
            # assert that the group role has been added to the user's group roles
            user_group_roles = [group_role for group_role in mock_user_data.group_roles]
            assert mock_group_role_data in user_group_roles

        @pytest.mark.asyncio
        async def test_should_throw_exception_when_user_not_in_group(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_group_role_data: models.GroupRole,
            mock_user_data: models.User,
        ) -> None:
            """Should throw exception when user not in group"""
            service = GroupRoleService(mock_db)

            mock_user_data.groups = []

            with pytest.raises(GroupNotFoundException):
                await service.assign(
                    mock_group_role_data,
                    mock_user_data,
                    mock_group_data,
                )

        @pytest.mark.asyncio
        async def test_should_throw_exception_when_group_role_not_in_group(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_group_role_data: models.GroupRole,
            mock_user_data: models.User,
        ) -> None:
            """Should throw exception when group role not in group"""
            service = GroupRoleService(mock_db)

            mock_group_data.roles = []

            with pytest.raises(GroupRoleNotFoundException):
                await service.assign(
                    mock_group_role_data,
                    mock_user_data,
                    mock_group_data,
                )

    class TestRemove:
        @pytest.mark.asyncio
        async def test_should_return_none_when_successful(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_group_role_data: models.GroupRole,
            mock_user_data: models.User,
        ) -> None:
            """Should return None when remove is successful"""
            service = GroupRoleService(mock_db)
            result: None = await service.remove(  # type: ignore[func-returns-value]
                mock_group_role_data,
                mock_user_data,
                mock_group_data,
            )
            assert result is None

        @pytest.mark.asyncio
        async def test_should_remove_group_role_from_user_service_account_when_successful(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_group_role_data: models.GroupRole,
            mock_user_data: models.User,
        ) -> None:
            """Should remove group role from user service account successful"""

            service = GroupRoleService(mock_db)
            await service.remove(
                mock_group_role_data,
                mock_user_data,
                mock_group_data,
            )

            # assert that the group role has been removed from the user's service accounts
            service_account_group_roles = [
                group_role
                for service_account in mock_user_data.service_accounts
                for group_role in service_account.group_roles
            ]
            assert mock_group_role_data not in service_account_group_roles

        @pytest.mark.asyncio
        async def test_should_remove_group_role_from_user_when_successful(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_group_role_data: models.GroupRole,
            mock_user_data: models.User,
        ) -> None:
            """Should remove group role from user when successful"""

            service = GroupRoleService(mock_db)
            await service.remove(
                mock_group_role_data,
                mock_user_data,
                mock_group_data,
            )

            # assert that the group role has been removed from the user's group roles
            user_group_roles = [group_role for group_role in mock_user_data.group_roles]
            assert mock_group_role_data not in user_group_roles

        @pytest.mark.asyncio
        async def test_should_throw_exception_when_group_role_not_in_group(
            self,
            mock_db: AsyncMock,
            mock_group_data: models.Group,
            mock_group_role_data: models.GroupRole,
            mock_user_data: models.User,
        ) -> None:
            """Should throw exception when group role not in group"""
            service = GroupRoleService(mock_db)

            mock_group_data.roles = []

            with pytest.raises(GroupRoleNotFoundException):
                await service.remove(
                    mock_group_role_data,
                    mock_user_data,
                    mock_group_data,
                )

    class TestCreate:
        @pytest.mark.asyncio
        async def test_should_return_group_role_when_successful(
            self,
            mock_db: AsyncMock,
            mock_permissions_data: list[models.Permission],
            mock_group_id: uuid.UUID = uuid.uuid4(),
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return a group role when successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.create(
                mock_group_role_name,
                mock_permissions_data,
                mock_group_id,
            )
            assert isinstance(group_role, models.GroupRole)

        @pytest.mark.asyncio
        async def test_should_create_group_role_that_matches_input_params_when_successful(
            self,
            mock_db: AsyncMock,
            mock_permissions_data: list[models.Permission],
            mock_group_id: uuid.UUID = uuid.uuid4(),
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return group with correct parameters when successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.create(
                mock_group_role_name,
                mock_permissions_data,
                mock_group_id,
            )
            assert group_role.name == mock_group_role_name
            assert group_role.group_id == mock_group_id
            assert group_role.permissions == mock_permissions_data

    class TestUpdate:
        @pytest.mark.asyncio
        async def test_should_return_group_role_when_successful(
            self,
            mock_db: AsyncMock,
            mock_permissions_data: list[models.Permission],
            mock_group_role_data: models.GroupRole,
            mock_group_data: models.Group,
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return a group role when successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.update(
                mock_group_role_name,
                mock_permissions_data,
                mock_group_role_data,
                mock_group_data,
            )
            assert isinstance(group_role, models.GroupRole)

        @pytest.mark.asyncio
        async def test_should_update_group_role_that_matches_input_params_when_successful(
            self,
            mock_db: AsyncMock,
            mock_permissions_data: list[models.Permission],
            mock_group_role_data: models.GroupRole,
            mock_group_data: models.Group,
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return group with correct parameters when successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.update(
                mock_group_role_name,
                mock_permissions_data,
                mock_group_role_data,
                mock_group_data,
            )
            assert group_role.permissions == mock_permissions_data
            assert group_role.name == mock_group_role_name

        @pytest.mark.asyncio
        async def test_should_throw_when_group_role_not_in_group(
            self,
            mock_db: AsyncMock,
            mock_permissions_data: list[models.Permission],
            mock_group_role_data: models.GroupRole,
            mock_group_data: models.Group,
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return a group role when successful"""
            mock_group_data.roles = []

            service = GroupRoleService(mock_db)
            with pytest.raises(GroupRoleNotFoundException):
                await service.update(
                    mock_group_role_name,
                    mock_permissions_data,
                    mock_group_role_data,
                    mock_group_data,
                )

    class TestDelete:
        @pytest.mark.asyncio
        async def test_should_call_db_delete_when_successful(
            self,
            mock_db: AsyncSession,
            mock_group_role_data: models.GroupRole,
        ) -> None:
            """Should call db delete when successful"""
            service = GroupRoleService(mock_db)
            await service.delete(mock_group_role_data)
            mock_db.delete.assert_called_with(mock_group_role_data)  # type: ignore[attr-defined]
