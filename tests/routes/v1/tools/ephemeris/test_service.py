from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from across_server.routes.v1.observatory import schemas as observatory_schemas
from across_server.routes.v1.observatory.exceptions import ObservatoryNotFoundException
from across_server.routes.v1.observatory.service import ObservatoryService
from across_server.routes.v1.tle.exceptions import TLENotFoundException
from across_server.routes.v1.tle.service import TLEService
from across_server.routes.v1.tools.ephemeris.exceptions import (
    EphemerisOutsideOperationalRangeException,
    NoEphemerisTypesFoundException,
)
from across_server.routes.v1.tools.ephemeris.service import EphemerisService


class TestEphemerisServiceTLE:
    @pytest.mark.asyncio
    async def test_get_tle_ephem_success(
        self,
        mock_db: AsyncMock,
        tle_parameters: observatory_schemas.TLEParameters,
        test_date_range: dict[str, datetime],
        mock_tle_data: dict[str, Any],
        mock_ephemeris: MagicMock,
    ) -> None:
        """Should successfully compute TLE ephemeris when valid parameters are provided"""

        # Mock TLE service and model
        mock_tle_model = MagicMock()
        mock_tle_model.__dict__ = mock_tle_data

        with (
            patch.object(TLEService, "__init__", return_value=None),
            patch.object(TLEService, "get", return_value=mock_tle_model),
            patch("anyio.to_thread.run_sync") as mock_run_sync,
        ):
            mock_run_sync.return_value = mock_ephemeris

            service = EphemerisService(mock_db)
            result = await service.get_tle_ephem(
                tle_parameters, test_date_range["begin"], test_date_range["end"]
            )

            assert result == mock_ephemeris
            mock_run_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tle_ephem_tle_not_found(
        self,
        mock_db: AsyncMock,
        tle_parameters: observatory_schemas.TLEParameters,
        test_date_range: dict[str, datetime],
    ) -> None:
        """Should raise TLENotFoundException when TLE is not found"""

        with (
            patch.object(TLEService, "__init__", return_value=None),
            patch.object(TLEService, "get", return_value=None),
        ):
            service = EphemerisService(mock_db)

            with pytest.raises(TLENotFoundException):
                await service.get_tle_ephem(
                    tle_parameters, test_date_range["begin"], test_date_range["end"]
                )


class TestEphemerisServiceJPL:
    @pytest.mark.asyncio
    async def test_get_jpl_ephem_success(
        self,
        mock_db: AsyncMock,
        jpl_parameters: observatory_schemas.JPLParameters,
        test_date_range: dict[str, datetime],
        mock_ephemeris: MagicMock,
    ) -> None:
        """Should successfully compute JPL ephemeris"""

        with patch("anyio.to_thread.run_sync") as mock_run_sync:
            mock_run_sync.return_value = mock_ephemeris

            service = EphemerisService(mock_db)
            result = await service.get_jpl_ephem(
                jpl_parameters, test_date_range["begin"], test_date_range["end"]
            )

            assert result == mock_ephemeris
            mock_run_sync.assert_called_once()


class TestEphemerisServiceSPICE:
    @pytest.mark.asyncio
    async def test_get_spice_ephem_success(
        self,
        mock_db: AsyncMock,
        spice_parameters: observatory_schemas.SPICEParameters,
        test_date_range: dict[str, datetime],
        mock_ephemeris: MagicMock,
    ) -> None:
        """Should successfully compute SPICE ephemeris"""

        with patch("anyio.to_thread.run_sync") as mock_run_sync:
            mock_run_sync.return_value = mock_ephemeris

            service = EphemerisService(mock_db)
            result = await service.get_spice_ephem(
                spice_parameters, test_date_range["begin"], test_date_range["end"]
            )

            assert result == mock_ephemeris
            mock_run_sync.assert_called_once()


class TestEphemerisServiceGround:
    @pytest.mark.asyncio
    async def test_get_ground_ephem_success(
        self,
        mock_db: AsyncMock,
        ground_parameters: observatory_schemas.GroundParameters,
        test_date_range: dict[str, datetime],
        mock_ephemeris: MagicMock,
    ) -> None:
        """Should successfully compute ground ephemeris"""

        with patch("anyio.to_thread.run_sync") as mock_run_sync:
            mock_run_sync.return_value = mock_ephemeris

            service = EphemerisService(mock_db)
            result = await service.get_ground_ephem(
                ground_parameters, test_date_range["begin"], test_date_range["end"]
            )

            assert result == mock_ephemeris
            mock_run_sync.assert_called_once()


class TestEphemerisServiceGet:
    @pytest.mark.asyncio
    async def test_get_observatory_not_found(
        self,
        mock_db: AsyncMock,
        test_observatory_id: UUID,
        test_date_range: dict[str, datetime],
    ) -> None:
        """Should raise ObservatoryNotFoundException when observatory is not found"""

        with (
            patch.object(ObservatoryService, "__init__", return_value=None),
            patch.object(ObservatoryService, "get", return_value=None),
        ):
            service = EphemerisService(mock_db)

            with pytest.raises(ObservatoryNotFoundException):
                await service.get(
                    test_observatory_id,
                    test_date_range["begin"],
                    test_date_range["end"],
                )

    @pytest.mark.asyncio
    async def test_get_outside_operational_range(
        self,
        mock_db: AsyncMock,
        test_observatory_id: UUID,
        test_date_range: dict[str, datetime],
        mock_observatory_model_with_operational: MagicMock,
        mock_tle_data: dict[str, Any],
    ) -> None:
        """Should raise EphemerisOutsideOperationalRangeException when date range is outside operational range"""

        # Mock TLE service and model
        mock_tle_model = MagicMock()
        mock_tle_model.__dict__ = mock_tle_data

        with (
            patch.object(ObservatoryService, "__init__", return_value=None),
            patch.object(
                ObservatoryService,
                "get",
                return_value=mock_observatory_model_with_operational,
            ),
            patch.object(TLEService, "__init__", return_value=None),
            patch.object(TLEService, "get", return_value=mock_tle_model),
        ):
            service = EphemerisService(mock_db)

            with pytest.raises(EphemerisOutsideOperationalRangeException):
                await service.get(
                    observatory_id=test_observatory_id,
                    date_range_begin=test_date_range["begin"],
                    date_range_end=test_date_range["end"],
                )

    @pytest.mark.asyncio
    async def test_get_no_ephemeris_types(
        self,
        mock_db: AsyncMock,
        test_observatory_id: UUID,
        test_date_range: dict[str, datetime],
        mock_observatory_model_no_ephemeris: MagicMock,
    ) -> None:
        """Should raise NoEphemerisTypesFoundException when no ephemeris types are found"""

        with (
            patch.object(ObservatoryService, "__init__", return_value=None),
            patch.object(
                ObservatoryService,
                "get",
                return_value=mock_observatory_model_no_ephemeris,
            ),
        ):
            service = EphemerisService(mock_db)

            with pytest.raises(NoEphemerisTypesFoundException):
                await service.get(
                    test_observatory_id,
                    test_date_range["begin"],
                    test_date_range["end"],
                )

    @pytest.mark.asyncio
    async def test_get_success_with_tle_ephemeris(
        self,
        mock_db: AsyncMock,
        test_observatory_id: UUID,
        test_date_range: dict[str, datetime],
        mock_observatory_model: MagicMock,
        mock_ephemeris: MagicMock,
    ) -> None:
        """Should successfully return TLE ephemeris when TLE ephemeris type is available"""

        with (
            patch.object(ObservatoryService, "__init__", return_value=None),
            patch.object(
                ObservatoryService, "get", return_value=mock_observatory_model
            ),
            patch.object(
                EphemerisService, "get_tle_ephem", return_value=mock_ephemeris
            ),
        ):
            service = EphemerisService(mock_db)
            result = await service.get(
                test_observatory_id, test_date_range["begin"], test_date_range["end"]
            )

            assert result == mock_ephemeris

    @pytest.mark.asyncio
    async def test_get_success_with_jpl_ephemeris(
        self,
        mock_db: AsyncMock,
        test_observatory_id: UUID,
        test_date_range: dict[str, datetime],
        mock_observatory_model: MagicMock,
        mock_ephemeris: MagicMock,
        jpl_ephemeris_type: observatory_schemas.ObservatoryEphemerisType,
    ) -> None:
        """Should successfully return JPL ephemeris when JPL ephemeris type is available"""

        # Modify mock observatory to have JPL ephemeris type
        mock_observatory_model.__dict__["ephemeris_types"] = [jpl_ephemeris_type]

        with (
            patch.object(ObservatoryService, "__init__", return_value=None),
            patch.object(
                ObservatoryService, "get", return_value=mock_observatory_model
            ),
            patch.object(
                EphemerisService, "get_jpl_ephem", return_value=mock_ephemeris
            ),
        ):
            service = EphemerisService(mock_db)
            result = await service.get(
                test_observatory_id, test_date_range["begin"], test_date_range["end"]
            )

            assert result == mock_ephemeris

    @pytest.mark.asyncio
    async def test_get_success_with_spice_ephemeris(
        self,
        mock_db: AsyncMock,
        test_observatory_id: UUID,
        test_date_range: dict[str, datetime],
        mock_observatory_model: MagicMock,
        mock_ephemeris: MagicMock,
        spice_ephemeris_type: observatory_schemas.ObservatoryEphemerisType,
    ) -> None:
        """Should successfully return SPICE ephemeris when SPICE ephemeris type is available"""

        # Modify mock observatory to have SPICE ephemeris type
        mock_observatory_model.__dict__["ephemeris_types"] = [spice_ephemeris_type]

        with (
            patch.object(ObservatoryService, "__init__", return_value=None),
            patch.object(
                ObservatoryService, "get", return_value=mock_observatory_model
            ),
            patch.object(
                EphemerisService, "get_spice_ephem", return_value=mock_ephemeris
            ),
        ):
            service = EphemerisService(mock_db)
            result = await service.get(
                test_observatory_id, test_date_range["begin"], test_date_range["end"]
            )

            assert result == mock_ephemeris

    @pytest.mark.asyncio
    async def test_get_success_with_ground_ephemeris(
        self,
        mock_db: AsyncMock,
        test_observatory_id: UUID,
        test_date_range: dict[str, datetime],
        mock_observatory_model: MagicMock,
        mock_ephemeris: MagicMock,
        ground_ephemeris_type: observatory_schemas.ObservatoryEphemerisType,
    ) -> None:
        """Should successfully return Ground ephemeris when Ground ephemeris type is available"""

        # Modify mock observatory to have Ground ephemeris type
        mock_observatory_model.__dict__["ephemeris_types"] = [ground_ephemeris_type]

        with (
            patch.object(ObservatoryService, "__init__", return_value=None),
            patch.object(
                ObservatoryService, "get", return_value=mock_observatory_model
            ),
            patch.object(
                EphemerisService, "get_ground_ephem", return_value=mock_ephemeris
            ),
        ):
            service = EphemerisService(mock_db)
            result = await service.get(
                test_observatory_id, test_date_range["begin"], test_date_range["end"]
            )

            assert result == mock_ephemeris
