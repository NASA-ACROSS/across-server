from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.routes.observation.exceptions import (
    InvalidObservationReadParametersException,
    ObservationNotFoundException,
)
from across_server.routes.observation.schemas import ObservationRead
from across_server.routes.observation.service import ObservationService


class TestObservationService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should raise ObservationNotFoundException when the observation does not exist"""
            mock_result.scalar_one_or_none.return_value = None

            service = ObservationService(mock_db)
            with pytest.raises(ObservationNotFoundException):
                await service.get(uuid4())

    class TestGetMany:
        @pytest.mark.asyncio
        async def test_should_return_empty_list_when_nothing_matches_params(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should return empty list when nothing matches params"""
            mock_result.scalars.all.return_value = []

            service = ObservationService(mock_db)
            params = ObservationRead()
            values = await service.get_many(params)
            assert len(values) == 0

        @pytest.mark.asyncio
        async def test_should_raise_422_with_bad_params(
            self, bad_observation_filter: Any, mock_db: AsyncMock
        ) -> None:
            """Should raise InvalidObservationReadParametersException with bad params"""

            service = ObservationService(mock_db)
            params = ObservationRead(**bad_observation_filter)
            with pytest.raises(InvalidObservationReadParametersException):
                await service.get_many(params)
