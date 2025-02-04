import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.routes.observation.service import ObservationService

from .conftest import MockObservationSchema


class TestObservationService:
    @pytest.mark.asyncio
    async def test_create_should_return_observation_when_successful(
        self, mock_db: AsyncSession, mock_observation: MockObservationSchema
    ) -> None:
        """Should return the observation when successful"""
        service = ObservationService(mock_db)
        observation = await service.create(mock_observation)  # type: ignore
        assert isinstance(observation, MockObservationSchema)

    @pytest.mark.asyncio
    async def test_create_should_save_observation_to_database(
        self, mock_db: AsyncSession, mock_observation: MockObservationSchema
    ) -> None:
        """Should save the observation to the database when successful"""
        service = ObservationService(mock_db)
        await service.create(mock_observation)  # type: ignore

        mock_db.commit.assert_called_once()  # type: ignore
