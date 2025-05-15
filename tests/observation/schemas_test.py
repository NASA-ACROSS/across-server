import pytest

from across_server.core.enums import InstrumentFOV
from across_server.core.exceptions import (
    RequiredFieldException,
)
from across_server.db.models import Observation as ObservationModel
from across_server.routes.observation.schemas import Observation, ObservationCreate


class TestObservationSchemas:
    @pytest.mark.asyncio
    async def test_from_orm_should_return_observation(
        self, mock_observation_data: ObservationModel
    ) -> None:
        """Should return the observation schema when successful"""
        observation = Observation.from_orm(mock_observation_data)
        assert isinstance(observation, Observation)

    @pytest.mark.asyncio
    async def test_to_orm_should_return_observation_model(
        self, mock_observation_create: ObservationCreate
    ) -> None:
        """Should return the observation model when successful"""
        observation_model = mock_observation_create.to_orm(InstrumentFOV.POLYGON)
        assert isinstance(observation_model, ObservationModel)

    @pytest.mark.asyncio
    async def test_to_orm_should_raise_required_pointing_position(
        self, mock_observation_create: ObservationCreate
    ) -> None:
        """Should raise exception when FOV is POINT or POLYGON and pointing position is None"""
        mock_observation_create.pointing_position = None
        with pytest.raises(RequiredFieldException):
            mock_observation_create.to_orm(InstrumentFOV.POLYGON)

    @pytest.mark.asyncio
    async def test_to_orm_should_return_observation_model_for_allsky_FOV_and_no_pointing(
        self, mock_observation_create: ObservationCreate
    ) -> None:
        """Should return the observation model when successful"""
        mock_observation_create.pointing_position = None
        observation_model = mock_observation_create.to_orm(InstrumentFOV.ALL_SKY)
        assert isinstance(observation_model, ObservationModel)
