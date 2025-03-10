import pytest

from across_server.core.exceptions import AcrossHTTPException, NotFoundException
from across_server.db import models
from across_server.routes.user.service_account.group_role.service import (
    ServiceAccountGroupRoleService,
)


class TestServiceAccountGroupRoleServiceAssign:
    @pytest.mark.asyncio
    async def test_assign_should_return_service_account_when_successful(
        self,
        mock_db,
        frozen_expiration,
        patch_datetime_now,
        mock_service_account_data,
        mock_group_role_data,
        mock_user_data,
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)
        service_account = await service.assign(
            mock_service_account_data,
            mock_group_role_data,
            mock_user_data,
        )
        assert isinstance(service_account, models.ServiceAccount)

    @pytest.mark.asyncio
    async def test_assign_should_throw_exception_when_service_account_is_none(
        self,
        mock_db,
        frozen_expiration,
        patch_datetime_now,
        mock_service_account_data,
        mock_group_role_data,
        mock_user_data,
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_service_account_data = None

        with pytest.raises(NotFoundException):
            await service.assign(
                mock_service_account_data,  # type: ignore
                mock_group_role_data,
                mock_user_data,
            )

    @pytest.mark.asyncio
    async def test_assign_should_throw_exception_when_service_account_expiration_is_none(
        self,
        mock_db,
        frozen_expiration,
        patch_datetime_now,
        mock_service_account_data,
        mock_group_role_data,
        mock_user_data,
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_service_account_data.expiration = None

        with pytest.raises(NotFoundException):
            await service.assign(
                mock_service_account_data,
                mock_group_role_data,
                mock_user_data,
            )

    @pytest.mark.asyncio
    async def test_assign_should_throw_exception_when_service_account_is_expired(
        self,
        frozen_expiration,
        patch_datetime_now,
        mock_db,
        mock_service_account_data,
        mock_group_role_data,
        mock_user_data,
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        # mock expiration minus 3 days from frozen datettime patch
        mock_service_account_data.expiration = frozen_expiration

        with pytest.raises(AcrossHTTPException):
            await service.assign(
                mock_service_account_data,
                mock_group_role_data,
                mock_user_data,
            )

    @pytest.mark.asyncio
    async def test_assign_should_throw_exception_when_group_role_is_none(
        self,
        frozen_expiration,
        patch_datetime_now,
        mock_db,
        mock_service_account_data,
        mock_group_role_data,
        mock_user_data,
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_group_role_data = None

        with pytest.raises(NotFoundException):
            await service.assign(
                mock_service_account_data,
                mock_group_role_data,  # type: ignore
                mock_user_data,
            )

    @pytest.mark.asyncio
    async def test_assign_should_throw_exception_when_user_is_none(
        self,
        frozen_expiration,
        patch_datetime_now,
        mock_db,
        mock_service_account_data,
        mock_group_role_data,
        mock_user_data,
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_user_data = None

        with pytest.raises(NotFoundException):
            await service.assign(
                mock_service_account_data,
                mock_group_role_data,
                mock_user_data,  # type: ignore
            )

    @pytest.mark.asyncio
    async def test_assign_should_throw_exception_when_group_role_is_not_users(
        self,
        frozen_expiration,
        patch_datetime_now,
        mock_db,
        mock_service_account_data,
        mock_group_role_data,
        mock_user_data,
    ) -> None:
        """Should return the service_account when creation successful"""
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
        self, mock_db, mock_service_account_data, mock_group_role_data, mock_user_data
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_service_account_data.group_roles = [mock_group_role_data]

        service_account = await service.remove(
            mock_service_account_data, mock_group_role_data
        )
        assert isinstance(service_account, models.ServiceAccount)

    @pytest.mark.asyncio
    async def test_remove_should_return_service_account_when_group_role_is_not_in_service_account(
        self, mock_db, mock_service_account_data, mock_group_role_data, mock_user_data
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_service_account_data.group_roles = []

        service_account = await service.remove(
            mock_service_account_data, mock_group_role_data
        )
        assert isinstance(service_account, models.ServiceAccount)

    @pytest.mark.asyncio
    async def test_remove_should_throw_when_service_account_is_none(
        self, mock_db, mock_service_account_data, mock_group_role_data, mock_user_data
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_service_account_data = None

        with pytest.raises(NotFoundException):
            await service.remove(
                mock_service_account_data,  # type: ignore
                mock_group_role_data,
            )

    @pytest.mark.asyncio
    async def test_remove_should_throw_when_group_role_is_none(
        self, mock_db, mock_service_account_data, mock_group_role_data, mock_user_data
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountGroupRoleService(mock_db)

        mock_group_role_data = None

        with pytest.raises(NotFoundException):
            await service.remove(
                mock_service_account_data,
                mock_group_role_data,  # type: ignore
            )
