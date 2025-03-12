from unittest.mock import AsyncMock

import pytest

from across_server.core.exceptions import NotFoundException
from across_server.db import models
from across_server.routes.user.service_account.group_role.service import (
    ServiceAccountGroupRoleService,
)


class TestServiceAccountGroupRoleServiceAssign:
    @pytest.mark.asyncio
    async def test_assign_should_return_service_account_when_successful(
        self,
        mock_db: AsyncMock,
        mock_service_account_data: models.ServiceAccount,
        mock_group_role_data: models.GroupRole,
        mock_user_data: models.User,
    ) -> None:
        """Should return the service_account when assign is successful"""
        service = ServiceAccountGroupRoleService(mock_db)
        service_account = await service.assign(
            mock_service_account_data,
            mock_group_role_data,
            mock_user_data,
        )
        assert isinstance(service_account, models.ServiceAccount)

    @pytest.mark.asyncio
    async def test_assign_should_throw_exception_when_group_role_is_not_users(
        self,
        mock_db: AsyncMock,
        mock_service_account_data: models.ServiceAccount,
        mock_group_role_data: models.GroupRole,
        mock_user_data: models.User,
    ) -> None:
        """Should throw exception when group role is not users"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_user_data.group_roles = []

        with pytest.raises(NotFoundException):
            await service.assign(
                mock_service_account_data,
                mock_group_role_data,
                mock_user_data,
            )


class TestServiceAccountGroupRoleServiceRemove:
    @pytest.mark.asyncio
    async def test_remove_should_return_service_account_when_successful(
        self,
        mock_db: AsyncMock,
        mock_service_account_data: models.ServiceAccount,
        mock_group_role_data: models.GroupRole,
        mock_user_data: models.User,
    ) -> None:
        """Should return the service_account when remove is successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_service_account_data.group_roles = [mock_group_role_data]

        service_account = await service.remove(
            mock_service_account_data, mock_group_role_data
        )
        assert isinstance(service_account, models.ServiceAccount)

    @pytest.mark.asyncio
    async def test_remove_should_return_service_account_when_group_role_is_not_in_service_account(
        self,
        mock_db: AsyncMock,
        mock_service_account_data: models.ServiceAccount,
        mock_group_role_data: models.GroupRole,
        mock_user_data: models.User,
    ) -> None:
        """Should return service account when group role is not in service account"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_service_account_data.group_roles = []

        service_account = await service.remove(
            mock_service_account_data, mock_group_role_data
        )
        assert isinstance(service_account, models.ServiceAccount)
