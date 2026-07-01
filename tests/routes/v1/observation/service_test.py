from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.routes.v1.observation.exceptions import (
    InvalidObservationReadParametersException,
    ObservationNotFoundException,
)
from across_server.routes.v1.observation.schemas import (
    ContainsPointReadParams,
    ObservationRead,
)
from across_server.routes.v1.observation.service import ObservationService


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
            mock_result.scalars.return_value.all.return_value = []

            service = ObservationService(mock_db)
            params = ObservationRead()
            observations, total_count = await service.get_many(params)
            assert len(observations) == 0

        @pytest.mark.asyncio
        async def test_should_raise_422_with_bad_params(
            self, bad_observation_filter: Any, mock_db: AsyncMock
        ) -> None:
            """Should raise InvalidObservationReadParametersException with bad params"""

            service = ObservationService(mock_db)
            params = ObservationRead(**bad_observation_filter)
            with pytest.raises(InvalidObservationReadParametersException):
                await service.get_many(params)

    class TestGetOverlapPoint:
        @pytest.mark.asyncio
        async def test_should_return_empty_list_when_nothing_matches_params(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should return empty list when nothing matches params"""
            mock_result.scalars.return_value.all.return_value = []

            service = ObservationService(mock_db)
            params = ContainsPointReadParams(ra=123.456, dec=-87.65)
            observations, total_count = await service.get_contains_point(params)
            assert len(observations) == 0

        @pytest.mark.asyncio
        async def test_should_return_list_when_matches_found(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_data_with_footprint: Any,
        ) -> None:
            """Should return list of tuples when matches are found"""
            mock_result.scalars.return_value.all.return_value = [
                fake_observation_data_with_footprint
            ]

            service = ObservationService(mock_db)
            params = ContainsPointReadParams(ra=123.456, dec=-87.65)
            observations, total_count = await service.get_contains_point(params)
            assert len(observations) == 1

        @pytest.mark.asyncio
        async def test_should_raise_invalid_params_exception_with_bad_params(
            self, bad_point_overlap_filter: Any, mock_db: AsyncMock
        ) -> None:
            """Should raise InvalidObservationReadParametersException with bad params"""
            service = ObservationService(mock_db)
            params = ContainsPointReadParams(
                ra=123.456, dec=-87.65, **bad_point_overlap_filter
            )
            with pytest.raises(InvalidObservationReadParametersException):
                await service.get_contains_point(params)
