from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import astropy.units as u  # type: ignore
import pytest

from across_server.db.models import Instrument, Telescope
from across_server.routes.v1.instrument.exceptions import InstrumentNotFoundException
from across_server.routes.v1.telescope.exceptions import TelescopeNotFoundException
from across_server.routes.v1.tools.visibility_calculator.exceptions import (
    VisibilityConstraintsNotFoundException,
    VisibilityTypeNotImplementedException,
)
from across_server.routes.v1.tools.visibility_calculator.service import (
    VisibilityCalculatorService,
)


class TestVisibilityService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_visibility_with_minute_resolution_when_hi_res_is_true(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_date_range: tuple[datetime, datetime],
            fake_ephemeris_service_get: AsyncMock,
            fake_instrument_service_get: AsyncMock,
            fake_telescope_service_get: AsyncMock,
            mock_telescope_data: Telescope,
            fake_instrument_with_constraints: Instrument,
        ) -> None:
            """Should calculate ephemeris visibility with minute resolution when hi_res is True"""
            ra, dec = fake_coordinates
            date_range_begin, date_range_end = fake_date_range

            fake_telescope_service_get.return_value = mock_telescope_data
            fake_instrument_service_get.return_value = fake_instrument_with_constraints

            with patch(
                "across_server.routes.v1.tools.visibility_calculator.service.partial",
                MagicMock(),
            ) as mock_partial:
                service = VisibilityCalculatorService(mock_db)
                await service.calculate_windows(
                    ra=ra,
                    dec=dec,
                    instrument_id=fake_instrument_with_constraints.id,
                    date_range_begin=date_range_begin,
                    date_range_end=date_range_end,
                    hi_res=True,
                )
                expected_step_size = 60 * u.s  # type: ignore
                assert (
                    expected_step_size == mock_partial.call_args_list[0][1]["step_size"]
                )

        @pytest.mark.asyncio
        async def test_should_return_visibility_with_hour_resolution_when_hi_res_is_false(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_date_range: tuple[datetime, datetime],
            fake_ephemeris_service_get: AsyncMock,
            fake_instrument_service_get: AsyncMock,
            fake_telescope_service_get: AsyncMock,
            mock_telescope_data: Telescope,
            fake_instrument_with_constraints: Instrument,
        ) -> None:
            """Should calculate ephemeris visibility with hour resolution when hi_res is False"""

            ra, dec = fake_coordinates
            date_range_begin, date_range_end = fake_date_range

            fake_telescope_service_get.return_value = mock_telescope_data
            fake_instrument_service_get.return_value = fake_instrument_with_constraints

            with patch(
                "across_server.routes.v1.tools.visibility_calculator.service.partial",
                MagicMock(),
            ) as mock_partial:
                service = VisibilityCalculatorService(mock_db)
                await service.calculate_windows(
                    ra=ra,
                    dec=dec,
                    instrument_id=fake_instrument_with_constraints.id,
                    date_range_begin=date_range_begin,
                    date_range_end=date_range_end,
                    hi_res=False,
                )
                expected_step_size = 3600 * u.s  # type: ignore
                assert (
                    expected_step_size == mock_partial.call_args_list[0][1]["step_size"]
                )

        @pytest.mark.asyncio
        async def test_ephemeris_visibility_raises_exception_when_no_constraints(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_date_range: tuple[datetime, datetime],
            fake_ephemeris_service_get: AsyncMock,
            fake_instrument_without_constraints: Instrument,
            fake_instrument_service_get: AsyncMock,
            fake_telescope_service_get: AsyncMock,
            mock_telescope_data: Telescope,
        ) -> None:
            """Should raise VisibilityConstraintsNotFoundException when instrument has no constraints"""

            ra, dec = fake_coordinates
            date_range_begin, date_range_end = fake_date_range

            fake_telescope_service_get.return_value = mock_telescope_data
            fake_instrument_service_get.return_value = (
                fake_instrument_without_constraints
            )

            service = VisibilityCalculatorService(mock_db)

            with pytest.raises(VisibilityConstraintsNotFoundException):
                await service.calculate_windows(
                    ra=ra,
                    dec=dec,
                    instrument_id=fake_instrument_without_constraints.id,
                    date_range_begin=date_range_begin,
                    date_range_end=date_range_end,
                    hi_res=True,
                )

        @pytest.mark.asyncio
        async def test_get_should_raise_instrument_not_found_when_instrument_does_not_exist(
            self,
            monkeypatch: pytest.MonkeyPatch,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_instrument_id: UUID,
            fake_instrument_service_get: AsyncMock,
        ) -> None:
            """Should raise InstrumentNotFoundException when instrument does not exist"""

            ra, dec = fake_coordinates

            fake_instrument_service_get.return_value = None

            service = VisibilityCalculatorService(mock_db)

            with pytest.raises(InstrumentNotFoundException):
                await service.calculate_windows(
                    ra=ra,
                    dec=dec,
                    instrument_id=fake_instrument_id,
                    date_range_begin=datetime.now(),
                    date_range_end=datetime.now(),
                    hi_res=False,
                )

        @pytest.mark.asyncio
        async def test_get_should_raise_http_exception_when_instrument_has_no_telescope(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_instrument_id: UUID,
            fake_instrument_service_get: AsyncMock,
            fake_instrument_schema_from_orm: MagicMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should raise HTTPException when instrument has no associated telescope"""
            ra, dec = fake_coordinates

            fake_instrument_schema_from_orm.telescope = None

            service = VisibilityCalculatorService(mock_db)

            with pytest.raises(TelescopeNotFoundException):
                await service.calculate_windows(
                    ra=ra,
                    dec=dec,
                    instrument_id=fake_instrument_id,
                    date_range_begin=datetime.now(),
                    date_range_end=datetime.now(),
                    hi_res=False,
                )

        @pytest.mark.asyncio
        async def test_get_should_call_get_ephemeris_visibility_when_visibility_type_is_ephemeris(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_instrument_id: UUID,
            fake_instrument_service_get: AsyncMock,
            fake_instrument_schema_from_orm: MagicMock,
            fake_telescope_service_get: AsyncMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should call get_ephemeris_visibility when instrument visibility type is EPHEMERIS"""

            ra, dec = fake_coordinates

            mock_visibility_result = MagicMock()

            service = VisibilityCalculatorService(mock_db)
            service._calc_ephemeris_visibility = AsyncMock(  # type: ignore
                return_value=mock_visibility_result
            )

            result = await service.calculate_windows(
                ra=ra,
                dec=dec,
                instrument_id=fake_instrument_id,
                date_range_begin=datetime.now(),
                date_range_end=datetime.now(),
                hi_res=False,
            )

            assert result == mock_visibility_result

        @pytest.mark.asyncio
        async def test_get_should_raise_not_implemented_error_when_visibility_type_not_supported(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_instrument_id: UUID,
            fake_instrument_service_get: AsyncMock,
            fake_instrument_schema_from_orm: MagicMock,
            fake_telescope_service_get: AsyncMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should raise NotImplementedError when instrument visibility type is not supported"""

            ra, dec = fake_coordinates

            fake_instrument_schema_from_orm.visibility_type = "unsupported_type"

            service = VisibilityCalculatorService(mock_db)

            with pytest.raises(VisibilityTypeNotImplementedException) as exc_info:
                await service.calculate_windows(
                    ra=ra,
                    dec=dec,
                    instrument_id=fake_instrument_id,
                    date_range_begin=datetime.now(),
                    date_range_end=datetime.now(),
                    hi_res=False,
                )

            assert "Visibility type unsupported_type is not implemented" in str(
                exc_info.value
            )
