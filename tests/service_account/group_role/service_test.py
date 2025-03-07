import pytest

from across_server.db import models
from across_server.routes.user.service_account.group_role.service import (
    ServiceAccountGroupRoleService,
)


class TestServiceAccountGroupRoleService:
    @pytest.mark.asyncio
    async def test_create_should_return_service_account_when_successful(
        self, mock_db, mock_service_account_data, mock_group_role_data, mock_user_data
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)
        service_account = await service.assign(
            mock_service_account_data,
            mock_group_role_data,
            mock_user_data,
        )
        assert isinstance(service_account, models.ServiceAccount)
