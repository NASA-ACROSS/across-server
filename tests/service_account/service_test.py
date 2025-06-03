from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from across_server.auth.security import generate_secret_key
from across_server.db import models
from across_server.routes.user.service_account.exceptions import (
    ServiceAccountNotFoundException,
)
from across_server.routes.user.service_account.schemas import ServiceAccountCreate
from across_server.routes.user.service_account.service import ServiceAccountService


class TestServiceAccountService:
    def test_service_account_secret_key_should_match(
        self: Any,
        patch_secrets_token_hex: Any,
        mock_secrets_token_hex: Any,
        patch_config_secret: Any,
        patch_datetime_now: Any,
        fixed_expiration: datetime,
    ) -> None:
        """Service Account secret key generation test"""
        generated_secret = generate_secret_key()
        assert generated_secret.key == mock_secrets_token_hex[0]
        assert generated_secret.salt == mock_secrets_token_hex[1]
        assert (
            generated_secret.expiration.replace(tzinfo=timezone.utc) == fixed_expiration
        )

    @pytest.mark.asyncio
    async def test_create_should_return_service_account_when_successful(
        self,
        mock_db: AsyncMock,
        service_account_create_example: ServiceAccountCreate,
    ) -> None:
        """Should return the service_account when creation successful"""
        service = ServiceAccountService(mock_db)
        service_account, secret_key = await service.create(
            service_account_create_example, created_by_id=uuid4()
        )
        assert isinstance(service_account, models.ServiceAccount)
        assert isinstance(secret_key, str)

    @pytest.mark.asyncio
    async def test_create_should_save_service_account_to_database(
        self, mock_db: AsyncMock, service_account_create_example: ServiceAccountCreate
    ) -> None:
        """Should save the service_account to the database when successful"""
        service = ServiceAccountService(mock_db)
        await service.create(service_account_create_example, created_by_id=uuid4())

        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_not_found_exception_when_does_not_exist(
        self,
        mock_db: AsyncMock,
        mock_scalar_one_or_none: MagicMock,
        mock_result: MagicMock,
    ) -> None:
        """Should return False when the service account does not exist"""
        mock_scalar_one_or_none.return_value = None
        mock_result.scalar_one_or_none = mock_scalar_one_or_none
        mock_db.execute.return_value = mock_result

        service = ServiceAccountService(mock_db)
        with pytest.raises(ServiceAccountNotFoundException):
            await service.get(uuid4(), uuid4())
