from uuid import uuid4

import pytest

from across_server.auth.security import generate_secret_key
from across_server.db import models
from across_server.routes.user.service_account.exceptions import (
    ServiceAccountNotFoundException,
)
from across_server.routes.user.service_account.service import ServiceAccountService


class TestServiceAccountService:
    def test_service_account_secret_key_should_match(
        self, patch_datetime_now, patch_config_secret, baked_secret
    ):
        """Service Account secret key generation test"""
        generated_secret = generate_secret_key()
        assert generated_secret.key == baked_secret

    @pytest.mark.asyncio
    async def test_create_should_return_service_account_when_successful(
        self, mock_db, service_account_create_example
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountService(mock_db)
        service_account = await service.create(
            service_account_create_example, created_by_id=uuid4()
        )
        assert isinstance(service_account, models.ServiceAccount)

    @pytest.mark.asyncio
    async def test_create_should_save_service_account_to_database(
        self, mock_db, service_account_create_example
    ) -> None:
        """Should save the service_account to the database when successful"""
        service = ServiceAccountService(mock_db)
        await service.create(service_account_create_example, created_by_id=uuid4())

        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_not_found_exception_when_does_not_exist(
        self, mock_db, mock_scalar_one_or_none, mock_result
    ) -> None:
        """Should return False when the service account does not exist"""
        mock_scalar_one_or_none.return_value = None
        mock_result.scalar_one_or_none = mock_scalar_one_or_none
        mock_db.execute.return_value = mock_result

        service = ServiceAccountService(mock_db)
        with pytest.raises(ServiceAccountNotFoundException):
            await service.get(uuid4(), uuid4())
