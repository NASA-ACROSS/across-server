import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.db import models
from across_server.routes.v1.group.exceptions import GroupNotFoundException
from across_server.routes.v1.group.role.exceptions import GroupRoleNotFoundException
from across_server.routes.v1.group.role.service import (
    GroupRoleService,
)


class TestGroupRoleService:
    class TestAssign:
        @pytest.mark.asyncio
        async def test_should_return_group_role_when_successful(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_group_role: models.GroupRole,
            fake_user: models.User,
        ) -> None:
            """Should return the group role when assign is successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.assign(
                fake_group_role,
                fake_user,
                fake_group,
            )
            assert isinstance(group_role, models.GroupRole)

        @pytest.mark.asyncio
        async def test_should_add_group_role_to_user_when_successful(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_group_role: models.GroupRole,
            fake_user: models.User,
        ) -> None:
            """Should add group role to user when successful"""
            fake_user.group_roles = []

            service = GroupRoleService(mock_db)
            await service.assign(
                fake_group_role,
                fake_user,
                fake_group,
            )
            # assert that the group role has been added to the user's group roles
            user_group_roles = [group_role for group_role in fake_user.group_roles]
            assert fake_group_role in user_group_roles

        @pytest.mark.asyncio
        async def test_should_throw_exception_when_user_not_in_group(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_group_role: models.GroupRole,
            fake_user: models.User,
        ) -> None:
            """Should throw exception when user not in group"""
            service = GroupRoleService(mock_db)

            fake_user.groups = []

            with pytest.raises(GroupNotFoundException):
                await service.assign(
                    fake_group_role,
                    fake_user,
                    fake_group,
                )

        @pytest.mark.asyncio
        async def test_should_throw_exception_when_group_role_not_in_group(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_group_role: models.GroupRole,
            fake_user: models.User,
        ) -> None:
            """Should throw exception when group role not in group"""
            service = GroupRoleService(mock_db)

            fake_group.roles = []

            with pytest.raises(GroupRoleNotFoundException):
                await service.assign(
                    fake_group_role,
                    fake_user,
                    fake_group,
                )

    class TestRemove:
        @pytest.mark.asyncio
        async def test_should_return_none_when_successful(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_group_role: models.GroupRole,
            fake_user: models.User,
        ) -> None:
            """Should return None when remove is successful"""
            service = GroupRoleService(mock_db)
            result: None = await service.remove(  # type: ignore[func-returns-value]
                fake_group_role,
                fake_user,
                fake_group,
            )
            assert result is None

        @pytest.mark.asyncio
        async def test_should_remove_group_role_from_user_service_account_when_successful(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_group_role: models.GroupRole,
            fake_user: models.User,
        ) -> None:
            """Should remove group role from user service account successful"""

            service = GroupRoleService(mock_db)
            await service.remove(
                fake_group_role,
                fake_user,
                fake_group,
            )

            # assert that the group role has been removed from the user's service accounts
            service_account_group_roles = [
                group_role
                for service_account in fake_user.service_accounts
                for group_role in service_account.group_roles
            ]
            assert fake_group_role not in service_account_group_roles

        @pytest.mark.asyncio
        async def test_should_remove_group_role_from_user_when_successful(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_group_role: models.GroupRole,
            fake_user: models.User,
        ) -> None:
            """Should remove group role from user when successful"""

            service = GroupRoleService(mock_db)
            await service.remove(
                fake_group_role,
                fake_user,
                fake_group,
            )

            # assert that the group role has been removed from the user's group roles
            user_group_roles = [group_role for group_role in fake_user.group_roles]
            assert fake_group_role not in user_group_roles

        @pytest.mark.asyncio
        async def test_should_throw_exception_when_group_role_not_in_group(
            self,
            mock_db: AsyncMock,
            fake_group: models.Group,
            fake_group_role: models.GroupRole,
            fake_user: models.User,
        ) -> None:
            """Should throw exception when group role not in group"""
            service = GroupRoleService(mock_db)

            fake_group.roles = []

            with pytest.raises(GroupRoleNotFoundException):
                await service.remove(
                    fake_group_role,
                    fake_user,
                    fake_group,
                )

    class TestCreate:
        @pytest.mark.asyncio
        async def test_should_return_group_role_when_successful(
            self,
            mock_db: AsyncMock,
            fake_permissions: list[models.Permission],
            mock_group_id: uuid.UUID = uuid.uuid4(),
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return a group role when successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.create(
                mock_group_role_name,
                fake_permissions,
                mock_group_id,
            )
            assert isinstance(group_role, models.GroupRole)

        @pytest.mark.asyncio
        async def test_should_create_group_role_that_matches_input_params_when_successful(
            self,
            mock_db: AsyncMock,
            fake_permissions: list[models.Permission],
            mock_group_id: uuid.UUID = uuid.uuid4(),
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return group with correct parameters when successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.create(
                mock_group_role_name,
                fake_permissions,
                mock_group_id,
            )
            assert group_role.name == mock_group_role_name
            assert group_role.group_id == mock_group_id
            assert group_role.permissions == fake_permissions

    class TestUpdate:
        @pytest.mark.asyncio
        async def test_should_return_group_role_when_successful(
            self,
            mock_db: AsyncMock,
            fake_permissions: list[models.Permission],
            fake_group_role: models.GroupRole,
            fake_group: models.Group,
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return a group role when successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.update(
                mock_group_role_name,
                fake_permissions,
                fake_group_role,
                fake_group,
            )
            assert isinstance(group_role, models.GroupRole)

        @pytest.mark.asyncio
        async def test_should_update_group_role_that_matches_input_params_when_successful(
            self,
            mock_db: AsyncMock,
            fake_permissions: list[models.Permission],
            fake_group_role: models.GroupRole,
            fake_group: models.Group,
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return group with correct parameters when successful"""
            service = GroupRoleService(mock_db)
            group_role = await service.update(
                mock_group_role_name,
                fake_permissions,
                fake_group_role,
                fake_group,
            )
            assert group_role.permissions == fake_permissions
            assert group_role.name == mock_group_role_name

        @pytest.mark.asyncio
        async def test_should_throw_when_group_role_not_in_group(
            self,
            mock_db: AsyncMock,
            fake_permissions: list[models.Permission],
            fake_group_role: models.GroupRole,
            fake_group: models.Group,
            mock_group_role_name: str = "Test Group Role",
        ) -> None:
            """Should return a group role when successful"""
            fake_group.roles = []

            service = GroupRoleService(mock_db)
            with pytest.raises(GroupRoleNotFoundException):
                await service.update(
                    mock_group_role_name,
                    fake_permissions,
                    fake_group_role,
                    fake_group,
                )

    class TestDelete:
        @pytest.mark.asyncio
        async def test_should_call_db_delete_when_successful(
            self,
            mock_db: AsyncSession,
            fake_group_role: models.GroupRole,
        ) -> None:
            """Should call db delete when successful"""
            service = GroupRoleService(mock_db)
            await service.delete(fake_group_role)
            mock_db.delete.assert_called_with(fake_group_role)  # type: ignore[attr-defined]
