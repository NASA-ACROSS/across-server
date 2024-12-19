import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession


class MockInstrumentModelWithFootprint:
    footprints = True
    

class MockInstrumentModelWithoutFootprint:
    footprints = False


class MockHasFootprint:
    @staticmethod
    def scalar_one_or_none():
        return MockInstrumentModelWithFootprint
    

class MockHasNoFootprint:
    @staticmethod
    def scalar_one_or_none():
        return MockInstrumentModelWithoutFootprint
    

class MockWithoutInstrument:
    @staticmethod
    def scalar_one_or_none():
        return None


@pytest.fixture
def mock_db_session_return_true():
    mock = AsyncMock(AsyncSession)
    mock.execute = AsyncMock(
        return_value = MockHasFootprint
    )
    yield mock

@pytest.fixture
def mock_db_session_return_false():
    mock = AsyncMock(AsyncSession)
    mock.execute = AsyncMock(
        return_value = MockHasNoFootprint
    )
    yield mock

@pytest.fixture
def mock_db_session_return_none():
    mock = AsyncMock(AsyncSession)
    mock.execute = AsyncMock(
        return_value = MockWithoutInstrument
    )
    yield mock