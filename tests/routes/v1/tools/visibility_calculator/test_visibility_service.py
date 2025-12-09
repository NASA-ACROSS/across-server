from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import astropy.units as u  # type: ignore
import pytest

import across_server.routes.v1.tools.visibility_calculator.service as service_mod
from across_server.core.enums.visibility_type import VisibilityType
from across_server.routes.v1.instrument.schemas import Instrument as InstrumentSchema
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
            mock_ephemeris_service: AsyncMock,
            fake_instrument_with_constraints: InstrumentSchema,
            fake_observatory_id: UUID,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should calculate ephemeris visibility with minute resolution when hi_res is True"""
            ra, dec = fake_coordinates
            date_range_begin, date_range_end = fake_date_range

            mock_partial = MagicMock()
            monkeypatch.setattr(service_mod, "partial", mock_partial)

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)
            await service.calculate_windows(
                ra=ra,
                dec=dec,
                instrument=fake_instrument_with_constraints,
                observatory_id=fake_observatory_id,
                date_range_begin=date_range_begin,
                date_range_end=date_range_end,
                hi_res=True,
            )
            expected_step_size = 60 * u.s  # type: ignore
            assert expected_step_size == mock_partial.call_args_list[0][1]["step_size"]

        @pytest.mark.asyncio
        async def test_should_return_visibility_with_hour_resolution_when_hi_res_is_false(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_date_range: tuple[datetime, datetime],
            mock_ephemeris_service: AsyncMock,
            fake_instrument_with_constraints: InstrumentSchema,
            fake_observatory_id: UUID,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should calculate ephemeris visibility with hour resolution when hi_res is False"""

            ra, dec = fake_coordinates
            date_range_begin, date_range_end = fake_date_range

            mock_partial = MagicMock()
            monkeypatch.setattr(service_mod, "partial", mock_partial)

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)
            await service.calculate_windows(
                ra=ra,
                dec=dec,
                instrument=fake_instrument_with_constraints,
                observatory_id=fake_observatory_id,
                date_range_begin=date_range_begin,
                date_range_end=date_range_end,
                hi_res=False,
            )
            expected_step_size = 3600 * u.s  # type: ignore
            assert expected_step_size == mock_partial.call_args_list[0][1]["step_size"]

        @pytest.mark.asyncio
        async def test_ephemeris_visibility_raises_exception_when_no_constraints(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_date_range: tuple[datetime, datetime],
            mock_ephemeris_service: AsyncMock,
            fake_instrument_without_constraints: InstrumentSchema,
            fake_observatory_id: UUID,
        ) -> None:
            """Should raise VisibilityConstraintsNotFoundException when instrument has no constraints"""

            ra, dec = fake_coordinates
            date_range_begin, date_range_end = fake_date_range

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)

            with pytest.raises(VisibilityConstraintsNotFoundException):
                await service.calculate_windows(
                    ra=ra,
                    dec=dec,
                    instrument=fake_instrument_without_constraints,
                    observatory_id=fake_observatory_id,
                    date_range_begin=date_range_begin,
                    date_range_end=date_range_end,
                    hi_res=True,
                )

        @pytest.mark.asyncio
        async def test_get_should_call_get_ephemeris_visibility_when_visibility_type_is_ephemeris(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_observatory_id: UUID,
            mock_ephemeris_service: AsyncMock,
            fake_instrument_with_constraints: InstrumentSchema,
        ) -> None:
            """Should call get_ephemeris_visibility when instrument visibility type is EPHEMERIS"""

            ra, dec = fake_coordinates

            mock_visibility_result = MagicMock()

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)
            service._calc_ephemeris_visibility = AsyncMock(  # type: ignore
                return_value=mock_visibility_result
            )

            result = await service.calculate_windows(
                ra=ra,
                dec=dec,
                instrument=fake_instrument_with_constraints,
                observatory_id=fake_observatory_id,
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
            fake_observatory_id: UUID,
            mock_ephemeris_service: AsyncMock,
            fake_instrument_with_constraints: InstrumentSchema,
        ) -> None:
            """Should raise NotImplementedError when instrument visibility type is not supported"""

            ra, dec = fake_coordinates

            fake_instrument_with_constraints.visibility_type = VisibilityType.CUSTOM

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)

            with pytest.raises(VisibilityTypeNotImplementedException):
                await service.calculate_windows(
                    ra=ra,
                    dec=dec,
                    instrument=fake_instrument_with_constraints,
                    observatory_id=fake_observatory_id,
                    date_range_begin=datetime.now(),
                    date_range_end=datetime.now(),
                    hi_res=False,
                )

    class TestFindJointVisibility:
        @pytest.mark.asyncio
        async def test_find_joint_visibility_should_call_partial(
            self,
            mock_db: AsyncMock,
            mock_ephemeris_service: AsyncMock,
            fake_instrument_with_constraints: InstrumentSchema,
            fake_ephemeris_visibility_result: MagicMock,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should calculate joint visibility with partial"""

            mock_partial = MagicMock()
            monkeypatch.setattr(service_mod, "partial", mock_partial)

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)
            await service.find_joint_visibility(
                visibilities=[fake_ephemeris_visibility_result],
                instrument_ids=[fake_instrument_with_constraints.id],
            )
            mock_partial.assert_called_once()
