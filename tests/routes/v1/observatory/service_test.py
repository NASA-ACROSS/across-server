from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.core.enums import EphemerisType
from across_server.core.enums.observatory_type import ObservatoryType
from across_server.db import models
from across_server.routes.v1.observatory import schemas
from across_server.routes.v1.observatory.exceptions import (
    ObservatoryNotFoundException,
)
from across_server.routes.v1.observatory.schemas import ObservatoryRead
from across_server.routes.v1.observatory.service import ObservatoryService


class TestObservatoryService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should raise a not found exception when the observatory does not exist"""
            mock_result.scalar_one_or_none.return_value = None

            service = ObservatoryService(mock_db)
            with pytest.raises(ObservatoryNotFoundException):
                await service.get(uuid4())

    class TestGetMany:
        @pytest.mark.asyncio
        async def test_should_return_empty_list_when_nothing_matches_params(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should return an empty list when there are no matching observatories"""
            mock_result.scalars.all.return_value = []
            # mock_db.execute.return_value = mock_result

            service = ObservatoryService(mock_db)
            params = ObservatoryRead()
            values = await service.get_many(params)
            assert len(values) == 0

    @pytest.mark.asyncio
    class TestGetEphemParameters:
        async def test_fetch_jpl_parameters(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should fetch JPL parameters for observatory with JPL ephemeris type"""
            observatory = models.Observatory(id=uuid4())
            eph_type = models.ObservatoryEphemerisType(
                ephemeris_type=EphemerisType.JPL.value
            )
            observatory.ephemeris_types = [eph_type]

            jpl_params = models.JPLEphemerisParameters(observatory_id=observatory.id)
            mock_result.scalars.return_value = [jpl_params]
            mock_db.execute.return_value = mock_result

            service = ObservatoryService(mock_db)
            result = await service._get_ephem_parameters([observatory])

            assert len(result) == 1
            assert result[0].ephemeris_types[0].parameters == jpl_params

        async def test_fetch_tle_parameters(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should fetch TLE parameters for observatory with TLE ephemeris type"""
            # Setup observatory with TLE ephemeris type
            observatory = models.Observatory(id=uuid4())
            eph_type = models.ObservatoryEphemerisType(
                ephemeris_type=EphemerisType.TLE.value
            )
            observatory.ephemeris_types = [eph_type]

            tle_params = models.TLEParameters(observatory_id=observatory.id)
            mock_result.scalars.return_value = [tle_params]
            mock_db.execute.return_value = mock_result

            service = ObservatoryService(mock_db)
            result = await service._get_ephem_parameters([observatory])

            assert len(result) == 1
            assert result[0].ephemeris_types[0].parameters == tle_params

        async def test_fetch_spice_parameters(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should fetch SPICE parameters for observatory with SPICE ephemeris type"""
            # Setup observatory with SPICE ephemeris type
            observatory = models.Observatory(id=uuid4())
            eph_type = models.ObservatoryEphemerisType(
                ephemeris_type=EphemerisType.SPICE.value
            )
            observatory.ephemeris_types = [eph_type]

            spice_params = models.SpiceKernelParameters(observatory_id=observatory.id)
            mock_result.scalars.return_value = [spice_params]
            mock_db.execute.return_value = mock_result

            service = ObservatoryService(mock_db)
            result = await service._get_ephem_parameters([observatory])

            assert len(result) == 1
            assert result[0].ephemeris_types[0].parameters == spice_params

        async def test_fetch_multiple_parameter_types(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should fetch multiple parameter types for observatory with multiple ephemeris types"""
            observatory = models.Observatory(id=uuid4())
            eph_types = [
                models.ObservatoryEphemerisType(ephemeris_type=EphemerisType.JPL.value),
                models.ObservatoryEphemerisType(
                    ephemeris_type=EphemerisType.GROUND.value
                ),
            ]
            observatory.ephemeris_types = eph_types

            jpl_params = models.JPLEphemerisParameters(observatory_id=observatory.id)
            ground_params = models.EarthLocationParameters(
                observatory_id=observatory.id
            )

            def mock_execute(query: str) -> AsyncMock:
                if "jpl_ephemeris_parameters" in str(query).lower():
                    mock_result.scalars.return_value = [jpl_params]
                else:
                    mock_result.scalars.return_value = [ground_params]
                return mock_result

            mock_db.execute.side_effect = mock_execute

            service = ObservatoryService(mock_db)
            result = await service._get_ephem_parameters([observatory])

            assert len(result) == 1
            assert len(result[0].ephemeris_types) == 2

        async def test_unknown_ephemeris_type_raises_error(
            self, mock_db: AsyncMock
        ) -> None:
            """Should raise ValueError for unknown ephemeris type"""
            observatory = models.Observatory(id=uuid4())
            eph_type = models.ObservatoryEphemerisType(ephemeris_type="UNKNOWN")
            observatory.ephemeris_types = [eph_type]

            service = ObservatoryService(mock_db)
            with pytest.raises(ValueError, match="Unknown ephemeris type: UNKNOWN"):
                await service._get_ephem_parameters([observatory])

        @pytest.mark.asyncio
        async def test_should_return_observatory_when_exists(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should return observatory when it exists"""
            observatory_id = uuid4()
            observatory = models.Observatory(id=observatory_id)
            mock_result.scalar_one_or_none.return_value = observatory
            mock_db.execute.return_value = mock_result

            service = ObservatoryService(mock_db)
            result = await service.get(observatory_id)

            assert result.id == observatory_id

    @pytest.mark.asyncio
    class TestGetFilter:
        async def test_empty_filter_when_no_params(self) -> None:
            """Should return empty filter list when no params specified"""
            service = ObservatoryService(AsyncMock())
            params = schemas.ObservatoryRead()
            filters = service._get_filter(params)
            assert len(filters) == 0

        async def test_filter_by_created_on(self) -> None:
            """Should add created_on filter when param specified"""
            service = ObservatoryService(AsyncMock())
            created_on = datetime.now()
            params = schemas.ObservatoryRead(created_on=created_on)
            filters = service._get_filter(params)
            assert "observatory.created_on" in str(filters[0])

        async def test_filter_by_name(self) -> None:
            """Should add name filter when param specified"""
            service = ObservatoryService(AsyncMock())
            params = schemas.ObservatoryRead(name="test")
            filters = service._get_filter(params)
            assert len(filters) == 1

        async def test_filter_by_telescope_id(self) -> None:
            """Should add telescope_id filter when param specified"""
            service = ObservatoryService(AsyncMock())
            telescope_id = uuid4()
            params = schemas.ObservatoryRead(telescope_id=telescope_id)
            filters = service._get_filter(params)
            assert len(filters) == 1

        async def test_filter_by_telescope_name(self) -> None:
            """Should add telescope_name filter when param specified"""
            service = ObservatoryService(AsyncMock())
            params = schemas.ObservatoryRead(telescope_name="test")
            filters = service._get_filter(params)
            assert len(filters) == 1

        async def test_filter_by_ephemeris_type(self) -> None:
            """Should add ephemeris_type filter when param specified"""
            service = ObservatoryService(AsyncMock())
            params = schemas.ObservatoryRead(ephemeris_type=[EphemerisType.GROUND])
            filters = service._get_filter(params)
            assert len(filters) == 1

        async def test_filter_by_type(self) -> None:
            """Should add type filter when param specified"""
            service = ObservatoryService(AsyncMock())
            params = schemas.ObservatoryRead(type=ObservatoryType.GROUND_BASED)
            filters = service._get_filter(params)
            assert len(filters) == 1

        async def test_multiple_filters(self) -> None:
            """Should combine multiple filters when multiple params specified"""
            service = ObservatoryService(AsyncMock())
            params = schemas.ObservatoryRead(
                name="test",
                type=ObservatoryType.GROUND_BASED,
                telescope_id=uuid4(),
                ephemeris_type=[EphemerisType.GROUND],
            )
            filters = service._get_filter(params)
            assert len(filters) == 4
