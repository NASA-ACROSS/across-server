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

        @pytest.mark.asyncio
        async def test_should_return_observation_when_exists(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_data: Any,
        ) -> None:
            """Should return the observation when it exists"""
            mock_result.scalar_one_or_none.return_value = fake_observation_data

            service = ObservationService(mock_db)
            observation = await service.get(uuid4())

            assert observation == fake_observation_data

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

        @pytest.mark.asyncio
        async def test_should_return_observations(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_data: Any,
        ) -> None:
            """Should return observations when matches exist"""
            mock_result.scalar_one.return_value = 1
            mock_result.scalars.return_value.all.return_value = [fake_observation_data]

            service = ObservationService(mock_db)
            params = ObservationRead()
            observations, total_count = await service.get_many(params)

            assert len(observations) == 1

        @pytest.mark.asyncio
        async def test_should_return_total_count(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_data: Any,
        ) -> None:
            """Should return total count when matches exist"""
            mock_result.scalar_one.return_value = 1
            mock_result.scalars.return_value.all.return_value = [fake_observation_data]

            service = ObservationService(mock_db)
            params = ObservationRead()
            observations, total_count = await service.get_many(params)

            assert total_count == 1

        @pytest.mark.asyncio
        async def test_should_make_two_database_calls_for_base_case(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_data: Any,
        ) -> None:
            """Should make two database calls for base case"""
            mock_result.scalar_one.return_value = 1
            mock_result.scalars.return_value.all.return_value = [fake_observation_data]

            service = ObservationService(mock_db)
            params = ObservationRead()
            observations, total_count = await service.get_many(params)

            assert mock_db.execute.call_count == 2

        @pytest.mark.asyncio
        async def test_should_pre_resolve_instrument_ids_when_observatory_ids_given(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_data: Any,
        ) -> None:
            """Should pre-resolve observatory IDs to instrument IDs"""
            mock_result.scalar_one.return_value = 1
            mock_result.scalars.return_value.all.side_effect = [
                [uuid4()],  # pre-resolve
                [fake_observation_data],  # hydrate
            ]

            service = ObservationService(mock_db)
            params = ObservationRead(observatory_ids=[uuid4()])
            observations, total_count = await service.get_many(params)

            # pre-resolution is another call on top of the 2 standard db calls
            assert mock_db.execute.call_count == 3

        @pytest.mark.asyncio
        async def test_should_pre_resolve_instrument_ids_when_telescope_ids_given(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_data: Any,
        ) -> None:
            """Should pre-resolve telescope IDs to instrument IDs"""
            mock_result.scalar_one.return_value = 1
            mock_result.scalars.return_value.all.side_effect = [
                [uuid4()],  # pre-resolve
                [fake_observation_data],  # hydrate
            ]

            service = ObservationService(mock_db)
            params = ObservationRead(telescope_ids=[uuid4()])
            observations, total_count = await service.get_many(params)

            # pre-resolution is another call on top of the 2 standard db calls
            assert mock_db.execute.call_count == 3

        @pytest.mark.asyncio
        async def test_should_merge_instrument_ids_with_pre_resolved(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_pair: Any,
        ) -> None:
            """Should merge instrument_ids with pre-resolved IDs when both provided"""
            obs_A, obs_B, expected_ids = fake_observation_pair

            mock_result.scalar_one.return_value = 2
            mock_result.scalars.return_value.all.side_effect = [
                [obs_A.instrument_id],  # pre-resolve finds instrument A
                [obs_A, obs_B],  # hydrate returns both
            ]

            service = ObservationService(mock_db)
            params = ObservationRead(
                observatory_ids=[uuid4()],
                instrument_ids=[obs_B.instrument_id],
            )
            observations, total_count = await service.get_many(params)

            assert {o.instrument_id for o in observations} == expected_ids

        @pytest.mark.asyncio
        async def test_should_return_empty_when_pre_resolve_yields_no_instruments(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should return empty when pre-resolve yields no instruments"""
            mock_result.scalar_one.return_value = 0
            mock_result.scalars.return_value.all.side_effect = [
                [],  # pre-resolve: no instruments
                [],  # hydrate: no observations
            ]

            service = ObservationService(mock_db)
            params = ObservationRead(observatory_ids=[uuid4()])
            observations, total_count = await service.get_many(params)

            assert len(observations) == 0

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

        @pytest.mark.asyncio
        async def test_should_return_total_count_and_observations(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_data_with_footprint: Any,
        ) -> None:
            """Should return total count and observations when matches found"""
            mock_result.scalar_one.return_value = 1
            mock_result.scalars.return_value.all.return_value = [
                fake_observation_data_with_footprint,
            ]

            service = ObservationService(mock_db)
            params = ContainsPointReadParams(ra=123.456, dec=-87.65)
            observations, total_count = await service.get_contains_point(params)

            assert total_count == 1
