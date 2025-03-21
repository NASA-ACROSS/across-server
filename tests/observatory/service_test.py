from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.core.enums import EphemerisType
from across_server.db import models
from across_server.routes.observatory.exceptions import (
    ObservatoryNotFoundException,
)
from across_server.routes.observatory.schemas import ObservatoryRead
from across_server.routes.observatory.service import ObservatoryService


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
            async def test_ground_station_parameters(
                self, mock_db: AsyncMock, mock_result: AsyncMock
            ) -> None:
                """Should fetch earth location parameters for ground station"""
                observatory = models.Observatory(id=uuid4())
                observatory.ephemeris_types = [
                    models.ObservatoryEphemerisType(
                        ephemeris_type=EphemerisType.GROUND.value
                    )
                ]

                earth_params = models.EarthLocationParameters()
                mock_result.scalar_one_or_none.return_value = earth_params
                mock_db.execute.return_value = mock_result

                service = ObservatoryService(mock_db)
                result = await service._get_ephem_parameters(observatory)

                assert result.ephemeris_types[0].parameters == earth_params

            async def test_jpl_parameters(
                self, mock_db: AsyncMock, mock_result: AsyncMock
            ) -> None:
                """Should fetch JPL parameters"""
                observatory = models.Observatory(id=uuid4())
                observatory.ephemeris_types = [
                    models.ObservatoryEphemerisType(
                        ephemeris_type=EphemerisType.JPL.value
                    )
                ]

                jpl_params = models.JPLEphemerisParameters()
                mock_result.scalar_one_or_none.return_value = jpl_params
                mock_db.execute.return_value = mock_result

                service = ObservatoryService(mock_db)
                result = await service._get_ephem_parameters(observatory)

                assert result.ephemeris_types[0].parameters == jpl_params

            async def test_tle_parameters(
                self, mock_db: AsyncMock, mock_result: AsyncMock
            ) -> None:
                """Should fetch TLE parameters"""
                observatory = models.Observatory(id=uuid4())
                observatory.ephemeris_types = [
                    models.ObservatoryEphemerisType(
                        ephemeris_type=EphemerisType.TLE.value
                    )
                ]

                tle_params = models.TLEParameters()
                mock_result.scalar_one_or_none.return_value = tle_params
                mock_db.execute.return_value = mock_result

                service = ObservatoryService(mock_db)
                result = await service._get_ephem_parameters(observatory)

                assert result.ephemeris_types[0].parameters == tle_params

            async def test_spice_parameters(
                self, mock_db: AsyncMock, mock_result: AsyncMock
            ) -> None:
                """Should fetch SPICE parameters"""
                observatory = models.Observatory(id=uuid4())
                observatory.ephemeris_types = [
                    models.ObservatoryEphemerisType(
                        ephemeris_type=EphemerisType.SPICE.value
                    )
                ]

                spice_params = models.SpiceKernelParameters()
                mock_result.scalar_one_or_none.return_value = spice_params
                mock_db.execute.return_value = mock_result

                service = ObservatoryService(mock_db)
                result = await service._get_ephem_parameters(observatory)

                assert result.ephemeris_types[0].parameters == spice_params

            async def test_invalid_type_raises_error(self, mock_db: AsyncMock) -> None:
                """Should raise ValueError for invalid ephemeris type"""
                observatory = models.Observatory(id=uuid4())
                observatory.ephemeris_types = [
                    models.ObservatoryEphemerisType(ephemeris_type="INVALID")
                ]

                service = ObservatoryService(mock_db)
                with pytest.raises(ValueError, match="Unknown ephemeris type: INVALID"):
                    await service._get_ephem_parameters(observatory)

        @pytest.mark.asyncio
        class TestGetWithEphemParameters:
            async def test_returns_observatory_with_ephem_parameters(
                self, mock_db: AsyncMock, mock_result: AsyncMock
            ) -> None:
                """Should return observatory with populated ephemeris parameters"""
                # Arrange
                observatory_id = uuid4()
                observatory = models.Observatory(id=observatory_id)
                observatory.ephemeris_types = [
                    models.ObservatoryEphemerisType(
                        ephemeris_type=EphemerisType.GROUND.value
                    )
                ]
                mock_result.scalar_one_or_none.return_value = observatory
                mock_db.execute.return_value = mock_result

                service = ObservatoryService(mock_db)

                # Act
                result = await service.get(observatory_id)

                # Assert
                assert result == observatory
