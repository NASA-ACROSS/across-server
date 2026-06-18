from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import astropy.units as u  # type: ignore
import pytest
from across.tools.footprint.schemas import Pointing
from across.tools.visibility.constraints import PointingConstraint

import across_server.routes.v1.tools.visibility_calculator.service as service_mod
from across_server.core.enums.visibility_type import VisibilityType
from across_server.db.models import Observation
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

        @pytest.mark.asyncio
        async def test_get_should_get_pointing_constraints_if_instrument_observation_strategy_is_survey(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_observatory_id: UUID,
            mock_ephemeris_service: AsyncMock,
            fake_survey_instrument: InstrumentSchema,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should get pointing constraints if the instrument observation strategy is 'survey'"""

            ra, dec = fake_coordinates

            mock_partial = MagicMock()
            monkeypatch.setattr(service_mod, "partial", mock_partial)

            mock_get_pointing_constraint = AsyncMock(return_value=None)
            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)
            monkeypatch.setattr(
                service,
                "_get_pointing_constraint",
                mock_get_pointing_constraint,
            )

            await service.calculate_windows(
                ra=ra,
                dec=dec,
                instrument=fake_survey_instrument,
                observatory_id=fake_observatory_id,
                date_range_begin=datetime.now(),
                date_range_end=datetime.now(),
                hi_res=False,
            )

            mock_get_pointing_constraint.assert_called_once()

        @pytest.mark.asyncio
        async def test_get_should_use_pointing_constraints_for_survey_instruments(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            fake_observatory_id: UUID,
            mock_ephemeris_service: AsyncMock,
            fake_survey_instrument: InstrumentSchema,
            fake_pointing_constraint: PointingConstraint,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Should use pointing constraints for survey instruments"""

            fake_survey_instrument.constraints = []

            ra, dec = fake_coordinates

            mock_partial = MagicMock()
            monkeypatch.setattr(service_mod, "partial", mock_partial)

            mock_get_pointing_constraint = AsyncMock(
                return_value=fake_pointing_constraint
            )
            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)
            monkeypatch.setattr(
                service,
                "_get_pointing_constraint",
                mock_get_pointing_constraint,
            )

            await service.calculate_windows(
                ra=ra,
                dec=dec,
                instrument=fake_survey_instrument,
                observatory_id=fake_observatory_id,
                date_range_begin=datetime.now(),
                date_range_end=datetime.now(),
                hi_res=False,
            )

            assert [fake_pointing_constraint] == mock_partial.call_args_list[0][1][
                "constraints"
            ]

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

    class TestGetPointingConstraint:
        @pytest.mark.asyncio
        async def test_get_pointing_constraint_should_return_pointing_constraint(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            mock_result: AsyncMock,
            mock_ephemeris_service: AsyncMock,
            fake_survey_instrument: InstrumentSchema,
        ) -> None:
            """Should return a PointingConstraint object"""
            mock_result.scalars.return_value.all.return_value = []

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)

            ra, dec = fake_coordinates
            res = await service._get_pointing_constraint(
                fake_survey_instrument,
                datetime.now(),
                datetime.now(),
                ra,
                dec,
            )
            assert isinstance(res, PointingConstraint)

        @pytest.mark.asyncio
        async def test_get_pointing_constraint_should_query_for_observations(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            mock_result: AsyncMock,
            mock_ephemeris_service: AsyncMock,
            fake_survey_instrument: InstrumentSchema,
        ) -> None:
            """Should query the database for observations to build pointing constraints"""
            mock_result.scalars.return_value.all.return_value = []

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)

            ra, dec = fake_coordinates
            await service._get_pointing_constraint(
                fake_survey_instrument,
                datetime.now(),
                datetime.now(),
                ra,
                dec,
            )

            mock_db.execute.assert_called_once()

        @pytest.mark.asyncio
        async def test_get_pointing_constraint_should_return_if_instrument_has_no_footprint(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            mock_result: AsyncMock,
            mock_ephemeris_service: AsyncMock,
            fake_survey_instrument: InstrumentSchema,
        ) -> None:
            """Should return None if instrument has no footprint"""
            mock_result.scalars.return_value.all.return_value = []

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)

            ra, dec = fake_coordinates
            fake_survey_instrument.footprints = None
            res = await service._get_pointing_constraint(
                fake_survey_instrument,
                datetime.now(),
                datetime.now(),
                ra,
                dec,
            )

            assert res is None

        @pytest.mark.asyncio
        async def test_should_return_no_pointings_if_no_obs_found(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            mock_result: AsyncMock,
            mock_ephemeris_service: AsyncMock,
            fake_survey_instrument: InstrumentSchema,
        ) -> None:
            """
            Should return a PointingConstraint object with no pointings if no
            observations are found
            """
            mock_result.scalars.return_value.all.return_value = []

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)

            ra, dec = fake_coordinates
            res = await service._get_pointing_constraint(
                fake_survey_instrument,
                datetime.now(),
                datetime.now(),
                ra,
                dec,
            )
            assert len(res.pointings) == 0  # type: ignore[union-attr]

        @pytest.mark.asyncio
        async def test_should_create_pointings_when_observations_are_returned(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            mock_result: AsyncMock,
            mock_ephemeris_service: AsyncMock,
            fake_survey_instrument: InstrumentSchema,
            fake_observation_data: Observation,
        ) -> None:
            """Should create pointings when observations are returned"""
            mock_result.scalars.return_value.all.return_value = [fake_observation_data]

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)

            ra, dec = fake_coordinates
            res = await service._get_pointing_constraint(
                fake_survey_instrument,
                datetime.now(),
                datetime.now(),
                ra,
                dec,
            )
            assert len(res.pointings) > 0  # type: ignore[union-attr]

        @pytest.mark.asyncio
        async def test_should_convert_observations_to_pointings(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            mock_result: AsyncMock,
            mock_ephemeris_service: AsyncMock,
            fake_survey_instrument: InstrumentSchema,
            fake_observation_data: Observation,
        ) -> None:
            """Should convert retrieved observations to pointings"""
            mock_result.scalars.return_value.all.return_value = [fake_observation_data]

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)

            ra, dec = fake_coordinates
            res = await service._get_pointing_constraint(
                fake_survey_instrument,
                datetime.now(),
                datetime.now(),
                ra,
                dec,
            )
            assert isinstance(res.pointings[0], Pointing)  # type: ignore[union-attr]

        @pytest.mark.asyncio
        async def test_should_create_pointings_from_observation_parameters(
            self,
            mock_db: AsyncMock,
            fake_coordinates: tuple[float, float],
            mock_result: AsyncMock,
            mock_ephemeris_service: AsyncMock,
            fake_survey_instrument: InstrumentSchema,
            fake_observation_data: Observation,
        ) -> None:
            """Should create pointings from observation parameters"""
            mock_result.scalars.return_value.all.return_value = [fake_observation_data]

            service = VisibilityCalculatorService(mock_db, mock_ephemeris_service)

            ra, dec = fake_coordinates
            res = await service._get_pointing_constraint(
                fake_survey_instrument,
                datetime.now(),
                datetime.now(),
                ra,
                dec,
            )
            pointing = res.pointings[0]  # type: ignore[union-attr]
            assert all(
                [
                    pointing.start_time == fake_observation_data.date_range_begin,
                    pointing.end_time == fake_observation_data.date_range_end,
                ]
            )
