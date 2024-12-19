import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from across_server.routes.observation.service import ObservationService
from .conftest import MockObservationSchema


@pytest.mark.asyncio
async def test_should_return_observation_when_successful(
    mock_db_session: AsyncSession,
    mock_observation: MockObservationSchema
):
    """Should return the observation when successful"""
    service = ObservationService(mock_db_session)
    observation = await service.create(mock_observation)
    assert isinstance(observation, MockObservationSchema)


@pytest.mark.asyncio
async def test_should_save_observation_to_database(
    mock_db_session: AsyncSession,
    mock_observation: MockObservationSchema
):
    """Should save the observation to the database when successful"""
    service = ObservationService(mock_db_session)
    await service.create(mock_observation)

    mock_db_session.commit.assert_called_once()