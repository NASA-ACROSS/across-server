from uuid import uuid4
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from across_server.routes.instrument.service import InstrumentService


@pytest.mark.asyncio
async def test_should_return_true_when_footprint_exists(
    mock_db_session_return_true: AsyncSession
):
    """Should return True when a footprint for the instrument exists"""
    service = InstrumentService(mock_db_session_return_true)
    assert await service.has_footprint(uuid4())


@pytest.mark.asyncio
async def test_should_return_false_when_no_footprint_exists(
    mock_db_session_return_false: AsyncSession
):
    """Should return False when a footprint for the instrument does not exist"""
    service = InstrumentService(mock_db_session_return_false)
    assert await service.has_footprint(uuid4()) == False


@pytest.mark.asyncio
async def test_should_return_false_when_no_instrument_exists(
    mock_db_session_return_none: AsyncSession
):
    """Should return False when the instrument does not exist"""
    service = InstrumentService(mock_db_session_return_none)
    assert await service.has_footprint(uuid4()) == False