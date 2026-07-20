from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from across_server.db.models import BrokerAlert, BrokerEvent
from across_server.routes.v1.localization.schemas import (
    LocalizationCreate,
)
from across_server.routes.v1.localization.service import LocalizationService


class TestLocalizationService:
    class TestCreateMany:
        @pytest.mark.asyncio
        async def test_should_save_localizations_to_database(
            self,
            mock_db: AsyncMock,
            fake_localization_create_schema: LocalizationCreate,
            fake_broker_event_data: BrokerEvent,
            fake_broker_alert_data: BrokerAlert,
        ) -> None:
            """Should save the localizations to the database when successful"""
            service = LocalizationService(mock_db)
            await service.create_many(
                [fake_localization_create_schema],
                fake_broker_event_data,
                fake_broker_alert_data,
            )

            mock_db.commit.assert_called_once()

        @pytest.mark.asyncio
        async def test_should_return_list_of_uuids(
            self,
            mock_db: AsyncMock,
            fake_localization_create_schema: LocalizationCreate,
            fake_broker_event_data: BrokerEvent,
            fake_broker_alert_data: BrokerAlert,
        ) -> None:
            """Should return list of UUIDs when successful"""
            service = LocalizationService(mock_db)
            res = await service.create_many(
                [fake_localization_create_schema],
                fake_broker_event_data,
                fake_broker_alert_data,
            )

            assert all([isinstance(id, UUID) for id in res])
