from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.routes.v1.broker_event.exceptions import BrokerEventNotFoundException
from across_server.routes.v1.broker_event.schemas import BrokerEventReadParams
from across_server.routes.v1.broker_event.service import BrokerEventService


class TestBrokerEventService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """
            Should raise BrokerEventNotFoundException
            when the broker event does not exist
            """
            mock_result.scalar_one_or_none.return_value = None

            service = BrokerEventService(mock_db)
            with pytest.raises(BrokerEventNotFoundException):
                await service.get(uuid4())

    class TestGetMany:
        @pytest.mark.asyncio
        async def test_should_return_empty_list_when_nothing_matches_params(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should return empty list when nothing matches params"""
            mock_result.scalars.all.return_value = []

            service = BrokerEventService(mock_db)
            params = BrokerEventReadParams()
            values = await service.get_many(params)
            assert len(values) == 0
