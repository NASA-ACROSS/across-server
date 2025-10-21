from datetime import datetime
from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import anyio.to_thread
import pytest
from across.tools.ephemeris import (
    compute_ground_ephemeris,
    compute_jpl_ephemeris,
    compute_spice_ephemeris,
    compute_tle_ephemeris,
)

import across_server.routes.v1.tools.ephemeris.service as service_mod
from across_server.routes.v1.observatory import schemas as observatory_schemas
from across_server.routes.v1.observatory.exceptions import ObservatoryNotFoundException
from across_server.routes.v1.tle.exceptions import TLENotFoundException
from across_server.routes.v1.tools.ephemeris.exceptions import (
    EphemerisCalculationNotFound,
    EphemerisNotFound,
    EphemerisTypeNotFound,
)
from across_server.routes.v1.tools.ephemeris.service import EphemerisService


class TestEphemerisService:
    class TestTLE:
        @pytest.mark.asyncio
        async def test_should_raise_when_tle_not_found(
            self,
            mock_db: AsyncMock,
            fake_tle_parameters: observatory_schemas.TLEParameters,
            fake_date_range: dict[str, datetime],
            mock_tle_service: AsyncMock,
            mock_observatory_service: AsyncMock,
        ) -> None:
            """Should raise TLENotFoundException when TLE is not found"""
            mock_tle_service.get.return_value = None
            service = EphemerisService(
                mock_db, mock_tle_service, mock_observatory_service
            )

            with pytest.raises(TLENotFoundException):
                await service._get_tle_ephem(
                    fake_tle_parameters,
                    fake_date_range["begin"],
                    fake_date_range["end"],
                )

    class TestGet:
        @pytest.mark.asyncio
        async def test_should_error_when_observatory_not_found(
            self,
            mock_db: AsyncMock,
            fake_observatory_id: UUID,
            fake_date_range: dict[str, datetime],
            mock_tle_service: AsyncMock,
            mock_observatory_service: AsyncMock,
        ) -> None:
            """Should raise ObservatoryNotFoundException when observatory is not found"""
            service = EphemerisService(
                mock_db, mock_tle_service, mock_observatory_service
            )

            with pytest.raises(ObservatoryNotFoundException):
                await service.get(
                    fake_observatory_id,
                    fake_date_range["begin"],
                    fake_date_range["end"],
                )

        @pytest.mark.asyncio
        async def test_should_error_when_outside_operational_range(
            self,
            mock_db: AsyncMock,
            fake_observatory_id: UUID,
            fake_date_range: dict[str, datetime],
            fake_operational_date_range: observatory_schemas.NullableDateRange,
            fake_observatory_model: MagicMock,
            mock_tle_service: AsyncMock,
            mock_observatory_service: AsyncMock,
        ) -> None:
            """Should raise EphemerisNotFound when date range is outside operational range"""
            fake_observatory_model.operational_begin_date = (
                fake_operational_date_range.begin
            )
            fake_observatory_model.operational_end_date = (
                fake_operational_date_range.end
            )

            mock_observatory_service.get.return_value = fake_observatory_model
            service = EphemerisService(
                mock_db, mock_tle_service, mock_observatory_service
            )

            with pytest.raises(EphemerisNotFound):
                await service.get(
                    observatory_id=fake_observatory_id,
                    date_range_begin=fake_date_range["begin"],
                    date_range_end=fake_date_range["end"],
                )

        @pytest.mark.asyncio
        async def test_should_error_when_no_ephemeris_types_found(
            self,
            mock_db: AsyncMock,
            fake_observatory_id: UUID,
            fake_date_range: dict[str, datetime],
            fake_observatory_model: MagicMock,
            mock_tle_service: AsyncMock,
            mock_observatory_service: AsyncMock,
        ) -> None:
            """Should raise NoEphemerisTypesFoundException when no ephemeris types are found"""
            fake_observatory_model.ephemeris_types = []

            mock_observatory_service.get.return_value = fake_observatory_model
            service = EphemerisService(
                mock_db, mock_tle_service, mock_observatory_service
            )

            with pytest.raises(EphemerisTypeNotFound):
                await service.get(
                    fake_observatory_id,
                    fake_date_range["begin"],
                    fake_date_range["end"],
                )

        @pytest.mark.asyncio
        async def test_should_error_when_ephemeris_calculations_fail(
            self,
            mock_db: AsyncMock,
            fake_observatory_id: UUID,
            fake_date_range: dict[str, datetime],
            fake_observatory_model: MagicMock,
            mock_tle_service: AsyncMock,
            mock_observatory_service: AsyncMock,
        ) -> None:
            """Should raise EphemerisCalculationNotFound when ephemeris calculations all fail"""
            mock_observatory_service.get.return_value = fake_observatory_model
            mock_tle_service.get.return_value = None
            service = EphemerisService(
                mock_db, mock_tle_service, mock_observatory_service
            )

            with pytest.raises(EphemerisCalculationNotFound):
                await service.get(
                    fake_observatory_id,
                    fake_date_range["begin"],
                    fake_date_range["end"],
                )

        @pytest.mark.parametrize(
            ("fake_ephemeris_type", "expected_compute_fn"),
            [
                ("fake_tle_ephemeris_type", compute_tle_ephemeris),
                ("fake_jpl_ephemeris_type", compute_jpl_ephemeris),
                ("fake_spice_ephemeris_type", compute_spice_ephemeris),
                ("fake_ground_ephemeris_type", compute_ground_ephemeris),
            ],
        )
        @pytest.mark.asyncio
        async def test_should_call_correct_compute_fn_for_given_ephemeris_type(
            self,
            request: Any,
            fake_ephemeris_type: observatory_schemas.ObservatoryEphemerisType,
            expected_compute_fn: Callable,
            mock_db: AsyncMock,
            fake_observatory_id: UUID,
            fake_date_range: dict[str, datetime],
            fake_observatory_model: MagicMock,
            mock_tle_service: AsyncMock,
            mock_observatory_service: AsyncMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should call the correct compute fn given the ephemeris type"""
            fake_observatory_model.ephemeris_types = [
                request.getfixturevalue(fake_ephemeris_type)
            ]

            mock_observatory_service.get.return_value = fake_observatory_model

            mock_run_sync = AsyncMock(return_value=None)
            monkeypatch.setattr(anyio.to_thread, "run_sync", mock_run_sync)

            mock_partial = MagicMock()
            monkeypatch.setattr(service_mod, "partial", mock_partial)

            service = EphemerisService(
                mock_db, mock_tle_service, mock_observatory_service
            )
            await service.get(
                fake_observatory_id,
                fake_date_range["begin"],
                fake_date_range["end"],
            )
            assert expected_compute_fn in mock_partial.call_args_list[0][0]
