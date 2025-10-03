from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from across_server.routes.v1.observatory import schemas as observatory_schemas
from across_server.routes.v1.observatory.exceptions import ObservatoryNotFoundException
from across_server.routes.v1.tle.exceptions import TLENotFoundException
from across_server.routes.v1.tools.ephemeris.exceptions import (
    EphemerisNotFound,
    EphemerisTypeNotFound,
)
from across_server.routes.v1.tools.ephemeris.service import EphemerisService


class TestEphemerisService:
    class TestTLE:
        @pytest.mark.parametrize(
            ("fake_parameters", "ephemeris_method_name"),
            [
                ("fake_tle_parameters", "_get_tle_ephem"),
                ("fake_jpl_parameters", "_get_jpl_ephem"),
                ("fake_spice_parameters", "_get_spice_ephem"),
                ("fake_ground_parameters", "_get_ground_ephem"),
            ],
        )
        @pytest.mark.asyncio
        async def test_should_return_ephemeris_with_valid_parameters(
            self,
            request: Any,
            fake_parameters: Any,
            ephemeris_method_name: str,
            mock_db: AsyncMock,
            fake_date_range: dict[str, datetime],
            mock_ephemeris_result: MagicMock,
            fake_tle_service_get: AsyncMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should successfully compute all ephemerises when valid parameters are provided"""
            service = EphemerisService(mock_db)
            method = getattr(service, ephemeris_method_name)
            result = await method(
                request.getfixturevalue(fake_parameters),
                fake_date_range["begin"],
                fake_date_range["end"],
            )

            assert result == mock_ephemeris_result

        @pytest.mark.asyncio
        async def test_should_raise_when_tle_not_found(
            self,
            mock_db: AsyncMock,
            fake_tle_parameters: observatory_schemas.TLEParameters,
            fake_date_range: dict[str, datetime],
            fake_tle_service_get: AsyncMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should raise TLENotFoundException when TLE is not found"""

            fake_tle_service_get.return_value = None

            service = EphemerisService(mock_db)

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
            fake_observatory_service_get: AsyncMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should raise ObservatoryNotFoundException when observatory is not found"""
            service = EphemerisService(mock_db)

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
            fake_operational_date_range: observatory_schemas.DateRange,
            fake_observatory_model: MagicMock,
            fake_observatory_service_get: AsyncMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should raise EphemerisNotFound when date range is outside operational range"""

            fake_observatory_model.operational_begin_date = (
                fake_operational_date_range.begin
            )
            fake_observatory_model.operational_end_date = (
                fake_operational_date_range.end
            )

            fake_observatory_service_get.return_value = fake_observatory_model

            service = EphemerisService(mock_db)

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
            fake_observatory_service_get: AsyncMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should raise NoEphemerisTypesFoundException when no ephemeris types are found"""

            fake_observatory_model.ephemeris_types = []

            fake_observatory_service_get.return_value = fake_observatory_model

            service = EphemerisService(mock_db)

            with pytest.raises(EphemerisTypeNotFound):
                await service.get(
                    fake_observatory_id,
                    fake_date_range["begin"],
                    fake_date_range["end"],
                )

        @pytest.mark.parametrize(
            "fake_ephemeris_type",
            [
                ("fake_tle_ephemeris_type"),
                ("fake_jpl_ephemeris_type"),
                ("fake_spice_ephemeris_type"),
                ("fake_ground_ephemeris_type"),
            ],
        )
        @pytest.mark.asyncio
        async def test_should_return_ephemeris_when_successful_for_tle_ephemeris(
            self,
            request: Any,
            fake_ephemeris_type: observatory_schemas.ObservatoryEphemerisType,
            mock_db: AsyncMock,
            fake_observatory_id: UUID,
            fake_date_range: dict[str, datetime],
            fake_observatory_model: MagicMock,
            mock_ephemeris_result: MagicMock,
            fake_observatory_service_get: AsyncMock,
            fake_ephemeris_service_get: AsyncMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should successfully return TLE ephemeris when TLE ephemeris type is available"""
            fake_observatory_model.ephemeris_types = [
                request.getfixturevalue(fake_ephemeris_type)
            ]

            fake_observatory_service_get.return_value = fake_observatory_model
            fake_ephemeris_service_get.return_value = mock_ephemeris_result

            service = EphemerisService(mock_db)
            result = await service.get(
                fake_observatory_id, fake_date_range["begin"], fake_date_range["end"]
            )

            assert result == mock_ephemeris_result
