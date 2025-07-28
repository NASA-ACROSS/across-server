from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from across_server.auth.schemas import SecretKeySchema
from across_server.auth.security import generate_secret_key
from across_server.db import models
from across_server.routes.v1.user.service_account import schemas
from across_server.routes.v1.user.service_account.exceptions import (
    ServiceAccountNotFoundException,
)
from across_server.routes.v1.user.service_account.schemas import ServiceAccountCreate
from across_server.routes.v1.user.service_account.service import ServiceAccountService


class TestServiceAccountService:
    def test_service_account_secret_key_should_match(
        self: Any,
        mock_secrets_token_hex: Any,
        fixed_expiration: datetime,
    ) -> None:
        """Service Account secret key generation test"""
        generated_secret = generate_secret_key()
        assert generated_secret.key == mock_secrets_token_hex[0]
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
        service_account_secret = await service.create(
            service_account_create_example, created_by_id=uuid4()
        )
        assert isinstance(service_account_secret, schemas.ServiceAccountSecret)

    @pytest.mark.asyncio
    async def test_create_should_save_service_account_to_database(
        self,
        mock_db: AsyncMock,
        service_account_create_example: ServiceAccountCreate,
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
    ) -> None:
        """Should return False when the service account does not exist"""
        mock_scalar_one_or_none.return_value = None

        service = ServiceAccountService(mock_db)
        with pytest.raises(ServiceAccountNotFoundException):
            await service.get(uuid4(), uuid4())

    class TestRotateKey:
        @pytest.mark.asyncio
        async def test_should_generate_a_new_secret_key_when_rotating(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            mock_service_account_record: models.ServiceAccount,
            mock_generate_secret_key: MagicMock,
        ) -> None:
            """Should generate a new secret key when rotating"""
            mock_scalar_one_or_none.return_value = mock_service_account_record

            service = ServiceAccountService(mock_db)

            await service.rotate_key(uuid4(), uuid4())

            mock_generate_secret_key.assert_called_once_with(
                expiration_duration=mock_service_account_record.expiration_duration
            )

        @pytest.mark.asyncio
        async def test_should_hash_the_new_secret_key_when_rotating(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            mock_service_account_record: models.ServiceAccount,
            mock_password_hasher: MagicMock,
            mock_secret_key_schema: SecretKeySchema,
        ) -> None:
            """Should hash a new secret key when rotating"""
            mock_scalar_one_or_none.return_value = mock_service_account_record

            service = ServiceAccountService(mock_db)

            await service.rotate_key(uuid4(), uuid4())

            mock_password_hasher.hash.assert_called_once_with(
                mock_secret_key_schema.key
            )

        @pytest.mark.asyncio
        async def test_should_save_the_new_secret_key_when_rotating(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            mock_service_account_record: models.ServiceAccount,
            mock_generate_secret_key: MagicMock,
        ) -> None:
            """Should save the new secret key when rotating"""
            mock_scalar_one_or_none.return_value = mock_service_account_record
            mock_key: str = "new secret key"
            mock_generate_secret_key.return_value.key = mock_key

            service = ServiceAccountService(mock_db)

            updated_sa = await service.rotate_key(uuid4(), uuid4())

            assert updated_sa.secret_key is not None
            assert mock_key in updated_sa.secret_key
