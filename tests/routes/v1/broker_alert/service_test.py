from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.db.models import (
    BrokerAlert as BrokerAlertModel,
)
from across_server.db.models import (
    BrokerEvent as BrokerEventModel,
)
from across_server.routes.v1.broker_alert.exceptions import (
    BrokerAlertNotFoundException,
    DuplicateBrokerAlertException,
)
from across_server.routes.v1.broker_alert.schemas import (
    BrokerAlertCreate,
    BrokerAlertReadParams,
)
from across_server.routes.v1.broker_alert.service import BrokerAlertService


class TestBrokerAlertService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """
            Should raise BrokerAlertNotFoundException
            when the broker event does not exist
            """
            mock_result.scalar_one_or_none.return_value = None

            service = BrokerAlertService(mock_db)
            with pytest.raises(BrokerAlertNotFoundException):
                await service.get(uuid4())

        @pytest.mark.asyncio
        async def test_should_return_broker_alert_when_successful(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_broker_alert_data: BrokerAlertModel,
        ) -> None:
            """
            Should return a broker alert when it is found
            """
            mock_result.scalar_one_or_none.return_value = fake_broker_alert_data

            service = BrokerAlertService(mock_db)
            res = await service.get(uuid4())
            assert isinstance(res, BrokerAlertModel)

    class TestGetMany:
        @pytest.mark.asyncio
        async def test_should_return_empty_list_when_nothing_matches_params(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should return empty list when nothing matches params"""
            mock_result.scalars.all.return_value = []

            service = BrokerAlertService(mock_db)
            params = BrokerAlertReadParams()
            values = await service.get_many(params)
            assert len(values) == 0

    class TestCreate:
        @pytest.mark.asyncio
        async def test_should_raise_duplicate_exception(
            self,
            mock_db: AsyncMock,
            fake_broker_alert_create_schema: BrokerAlertCreate,
            fake_broker_event_data: BrokerEventModel,
            mock_result: AsyncMock,
            fake_broker_alert_data: BrokerAlertModel,
        ) -> None:
            """Should raise DuplicateBrokerAlertException if broker alert already exists"""
            mock_result.scalars.return_value.all.return_value = [
                fake_broker_alert_data,
            ]
            service = BrokerAlertService(mock_db)

            with pytest.raises(DuplicateBrokerAlertException):
                await service.create(
                    fake_broker_alert_create_schema,
                    fake_broker_event_data,
                )

        @pytest.mark.asyncio
        async def test_should_save_broker_alert_to_database(
            self,
            mock_db: AsyncMock,
            fake_broker_alert_create_schema: BrokerAlertCreate,
            fake_broker_event_data: BrokerEventModel,
            mock_result: AsyncMock,
        ) -> None:
            """Should save the broker alert to the database when successful"""
            mock_result.scalars.return_value.all.return_value = []
            service = BrokerAlertService(mock_db)
            await service.create(
                fake_broker_alert_create_schema,
                fake_broker_event_data,
            )

            mock_db.commit.assert_called_once()

        @pytest.mark.asyncio
        async def test_should_create_broker_event_from_broker_alert_data(
            self,
            mock_db: AsyncMock,
            fake_broker_alert_create_schema: BrokerAlertCreate,
            fake_broker_event_data: BrokerEventModel,
            mock_result: AsyncMock,
        ) -> None:
            """Should create a broker event from the broker alert data"""
            mock_result.scalar_one_or_none.return_value = None
            service = BrokerAlertService(mock_db)

            await service.create(
                fake_broker_alert_create_schema,
                fake_broker_event_data,
            )

            call_args = mock_db.add.call_args_list[-1]

            # check that the broker event was created from the BrokerAlertCreate parameters
            assert (
                call_args[0][0].name
                == fake_broker_alert_create_schema.broker_event_name
            )
