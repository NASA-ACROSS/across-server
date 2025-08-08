from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from across_server.auth.schemas import SecretKeySchema
from across_server.db import models
from across_server.routes.v1.user.service_account import schemas
from across_server.routes.v1.user.service_account.exceptions import (
    ServiceAccountNotFoundException,
)
from across_server.routes.v1.user.service_account.schemas import ServiceAccountCreate
from across_server.routes.v1.user.service_account.service import ServiceAccountService


class TestServiceAccountService:
    class TestCreate:
        @pytest.fixture(autouse=True)
        def find_db_user(
            self, mock_scalar_result: MagicMock, fake_user: models.User
        ) -> None:
            mock_scalar_result.one.return_value(fake_user)

        @pytest.mark.asyncio
        async def should_generate_secret_key_hex_with_64_bytes(
            self: Any,
            mock_secrets_token_hex: MagicMock,
            service_account_create_example: ServiceAccountCreate,
            mock_db: AsyncMock,
        ) -> None:
            """should generate a secret key as hex with 64 bytes"""
            service = ServiceAccountService(mock_db)
            await service.create(service_account_create_example, created_by_id=uuid4())

            mock_secrets_token_hex.assert_called_once_with(64)

        @pytest.mark.asyncio
        async def should_return_the_expiration_date_of_the_key(
            self: Any,
            fixed_expiration: datetime,
            service_account_create_example: ServiceAccountCreate,
            mock_db: AsyncMock,
        ) -> None:
            """should return the expiration date of the key"""
            service = ServiceAccountService(mock_db)
            sa = await service.create(
                service_account_create_example, created_by_id=uuid4()
            )

            assert sa.expiration == fixed_expiration

        @pytest.mark.asyncio
        async def test_create_should_return_service_account_when_successful(
            self,
            mock_db: AsyncMock,
            fake_service_account_create: ServiceAccountCreate,
        ) -> None:
            """Should return the service_account when creation successful"""
            service = ServiceAccountService(mock_db)
            service_account_secret = await service.create(
                fake_service_account_create, created_by_id=uuid4()
            )
            assert isinstance(service_account_secret, schemas.ServiceAccountSecret)

        @pytest.mark.asyncio
        async def test_create_should_save_service_account_to_database(
            self,
            mock_db: AsyncMock,
            fake_service_account_create: ServiceAccountCreate,
        ) -> None:
            """Should save the service_account to the database when successful"""
            service = ServiceAccountService(mock_db)
            await service.create(fake_service_account_create, created_by_id=uuid4())

            mock_db.commit.assert_called_once()

    class TestRotateKey:
        @pytest.mark.asyncio
        async def test_should_generate_a_new_secret_key_when_rotating(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_service_account: models.ServiceAccount,
            mock_secrets: MagicMock,
        ) -> None:
            """Should generate a new secret key when rotating"""
            mock_scalar_one_or_none.return_value = fake_service_account

            service = ServiceAccountService(mock_db)

            await service.rotate_key(uuid4(), uuid4())

            mock_secrets.token_hex.assert_called_once()

        @pytest.mark.asyncio
        async def test_should_hash_the_new_secret_key_when_rotating(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_service_account: models.ServiceAccount,
            mock_password_hasher: MagicMock,
            fake_secret_key_schema: SecretKeySchema,
        ) -> None:
            """Should hash a new secret key when rotating"""
            mock_scalar_one_or_none.return_value = fake_service_account

            service = ServiceAccountService(mock_db)

            await service.rotate_key(uuid4(), uuid4())

            mock_password_hasher.hash.assert_called_once_with(
                fake_secret_key_schema.key
            )

        @pytest.mark.asyncio
        async def test_should_return_the_secret_key_when_rotating(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            fake_service_account: models.ServiceAccount,
            mock_secrets: MagicMock,
        ) -> None:
            """Should return the secret key when rotating"""
            mock_scalar_one_or_none.return_value = fake_service_account

            service = ServiceAccountService(mock_db)

            updated_sa = await service.rotate_key(uuid4(), uuid4())

            assert mock_secrets.token_hex.return_value == updated_sa.secret_key

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
