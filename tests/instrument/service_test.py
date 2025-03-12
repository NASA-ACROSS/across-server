from uuid import uuid4

import pytest

from across_server.routes.instrument.exceptions import InstrumentNotFoundException
from across_server.routes.instrument.schemas import InstrumentRead
from across_server.routes.instrument.service import InstrumentService


class TestInstrumentService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self, mock_db, mock_result
        ) -> None:
            """Should raise a not found exception when the instrument does not exist"""
            mock_result.scalar_one_or_none.return_value = None

            service = InstrumentService(mock_db)
            with pytest.raises(InstrumentNotFoundException):
                await service.get(uuid4())

        class TestGetMany:
            @pytest.mark.asyncio
            async def test_should_return_empty_list_when_nothing_matches_params(
                self, mock_db, mock_result
            ) -> None:
                """Should return False when the telescope does not exist"""
                mock_result.scalars.all.return_value = []

                service = InstrumentService(mock_db)
                params = InstrumentRead()
                values = await service.get_many(params)
                assert len(values) == 0


class MockInstrumentModelWithFootprint:
    footprints: list = ["footprint_1"]


class MockInstrumentModelWithoutFootprint:
    footprints: list = []


class TestInstrumentFootprintService:
    @pytest.mark.asyncio
    async def test_has_footprint_should_return_true_when_footprint_exists(
        self, mock_db, mock_scalar_one_or_none, mock_result
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
        assert await service.has_footprint(uuid4()) is False

    @pytest.mark.asyncio
    async def test_has_footprint_should_raise_exception_when_no_instrument_exists(
        self, mock_db, mock_scalar_one_or_none, mock_result
    ) -> None:
        """Should return False when the instrument does not exist"""
        mock_scalar_one_or_none.return_value = None
        mock_result.scalar_one_or_none = mock_scalar_one_or_none
        mock_db.execute.return_value = mock_result

        service = InstrumentService(mock_db)
        with pytest.raises(InstrumentNotFoundException):
            await service.has_footprint(uuid4())
