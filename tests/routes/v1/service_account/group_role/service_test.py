from unittest.mock import AsyncMock

import pytest

from across_server.core.exceptions import NotFoundException
from across_server.db import models
from across_server.routes.v1.user.service_account.group_role.service import (
    ServiceAccountGroupRoleService,
)


class TestServiceAccountGroupRoleServiceAssign:
    @pytest.mark.asyncio
    async def test_assign_should_return_service_account_when_successful(
        self,
        mock_db: AsyncMock,
        fake_service_account: models.ServiceAccount,
        fake_group_role: models.GroupRole,
        fake_user: models.User,
    ) -> None:
        """Should return the service_account when assign is successful"""
        service = ServiceAccountGroupRoleService(mock_db)
        service_account = await service.assign(
            fake_service_account,
            fake_group_role,
            fake_user,
        )
        assert isinstance(service_account, models.ServiceAccount)

    @pytest.mark.asyncio
    async def test_assign_should_throw_exception_when_group_role_is_not_users(
        self,
        mock_db: AsyncMock,
        fake_service_account: models.ServiceAccount,
        fake_group_role: models.GroupRole,
        fake_user: models.User,
    ) -> None:
        """Should throw exception when group role is not users"""
        service = ServiceAccountGroupRoleService(mock_db)

        fake_user.group_roles = []

        with pytest.raises(NotFoundException):
            await service.assign(
                fake_service_account,
                fake_group_role,
                fake_user,
            )


class TestServiceAccountGroupRoleServiceRemove:
    @pytest.mark.asyncio
    async def test_remove_should_return_service_account_when_successful(
        self,
        mock_db: AsyncMock,
        fake_service_account: models.ServiceAccount,
        fake_group_role: models.GroupRole,
    ) -> None:
        """Should return the service_account when remove is successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        fake_service_account.group_roles = [fake_group_role]

        service_account = await service.remove(fake_service_account, fake_group_role)

        assert len(service_account.group_roles) == 0

    @pytest.mark.asyncio
    async def test_remove_should_return_service_account_when_group_role_is_not_in_service_account(
        self,
        mock_db: AsyncMock,
        fake_service_account: models.ServiceAccount,
        fake_group_role: models.GroupRole,
    ) -> None:
        """Should return service account when group role is not in service account"""
        service = ServiceAccountGroupRoleService(mock_db)

        fake_service_account.group_roles = []

        service_account = await service.remove(fake_service_account, fake_group_role)

        assert isinstance(service_account, models.ServiceAccount)
