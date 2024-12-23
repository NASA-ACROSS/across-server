from uuid import uuid4
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from across_server.routes.instrument.service import InstrumentService


class MockInstrumentModelWithFootprint:
    footprints = ['footprint_1']
    

class MockInstrumentModelWithoutFootprint:
    footprints = []


class TestInstrumentFootprintService:

    @pytest.mark.asyncio
    async def test_has_footprint_should_return_true_when_footprint_exists(
        self,
        mock_db, 
        mock_scalar_one_or_none, 
        mock_result
    ) -> None:
        """Should return True when a footprint for the instrument exists"""
        mock_scalar_one_or_none.return_value = MockInstrumentModelWithFootprint
        mock_result.scalar_one_or_none = mock_scalar_one_or_none
        mock_db.execute.return_value = mock_result

        service = InstrumentService(mock_db)
        assert await service.has_footprint(uuid4())

    @pytest.mark.asyncio
    async def test_has_footprint_should_return_false_when_no_footprint_exists(
        self, mock_db, mock_scalar_one_or_none, mock_result
    ) -> None:
        """Should return False when a footprint for the instrument does not exist"""
        mock_scalar_one_or_none.return_value = MockInstrumentModelWithoutFootprint
        mock_result.scalar_one_or_none = mock_scalar_one_or_none
        mock_db.execute.return_value = mock_result
        
        service = InstrumentService(mock_db)
        assert await service.has_footprint(uuid4()) == False

    @pytest.mark.asyncio
    async def test_has_footprint_should_return_false_when_no_instrument_exists(
        self, mock_db, mock_scalar_one_or_none, mock_result
    ) -> None:
        """Should return False when the instrument does not exist"""
        mock_scalar_one_or_none.return_value = None
        mock_result.scalar_one_or_none = mock_scalar_one_or_none
        mock_db.execute.return_value = mock_result

        service = InstrumentService(mock_db)
        assert await service.has_footprint(uuid4()) == False