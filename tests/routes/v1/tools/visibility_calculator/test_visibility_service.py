from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from fastapi import HTTPException

from across_server.routes.v1.instrument.exceptions import InstrumentNotFoundException
from across_server.routes.v1.instrument.schemas import Instrument as InstrumentSchema
from across_server.routes.v1.tools.visibility_calculator.exceptions import (
    VisibilityConstraintsNotFoundException,
    VisibilityTypeNotImplementedException,
)
from across_server.routes.v1.tools.visibility_calculator.service import (
    VisibilityService,
)


class TestVisibilityService:
    @pytest.mark.asyncio
    async def test_get_ephemeris_visibility_with_hi_res_true(
        self,
        mock_db: AsyncMock,
        sample_coordinates: tuple[float, float],
        sample_observatory_id: UUID,
        sample_date_range: tuple[datetime, datetime],
        instrument_with_constraints: InstrumentSchema,
        mock_ephemeris_mocks: tuple[AsyncMock, AsyncMock, AsyncMock],
    ) -> None:
        """Should calculate ephemeris visibility with minute resolution when hi_res is True"""

        mock_ephemeris_service, _, mock_visibility_result = mock_ephemeris_mocks
        ra, dec = sample_coordinates
        date_range_begin, date_range_end = sample_date_range

        service = VisibilityService(mock_db)
        result = await service.get_ephemeris_visibility(
            ra=ra,
            dec=dec,
            instrument=instrument_with_constraints,
            observatory_id=sample_observatory_id,
            date_range_begin=date_range_begin,
            date_range_end=date_range_end,
            hi_res=True,
        )

        mock_ephemeris_service.get.assert_called_once()
        assert result == mock_visibility_result

    @pytest.mark.asyncio
    async def test_get_ephemeris_visibility_with_hi_res_false(
        self,
        mock_db: AsyncMock,
        sample_coordinates: tuple[float, float],
        sample_observatory_id: UUID,
        sample_date_range: tuple[datetime, datetime],
        instrument_with_constraints: InstrumentSchema,
        mock_ephemeris_mocks: tuple[AsyncMock, AsyncMock, AsyncMock],
    ) -> None:
        """Should calculate ephemeris visibility with hour resolution when hi_res is False"""

        mock_ephemeris_service, _, mock_visibility_result = mock_ephemeris_mocks
        ra, dec = sample_coordinates
        date_range_begin, date_range_end = sample_date_range

        service = VisibilityService(mock_db)
        result = await service.get_ephemeris_visibility(
            ra=ra,
            dec=dec,
            instrument=instrument_with_constraints,
            observatory_id=sample_observatory_id,
            date_range_begin=date_range_begin,
            date_range_end=date_range_end,
            hi_res=False,
        )

        mock_ephemeris_service.get.assert_called_once()
        assert result == mock_visibility_result

    @pytest.mark.asyncio
    async def test_get_ephemeris_visibility_raises_exception_when_no_constraints(
        self,
        mock_db: AsyncMock,
        sample_coordinates: tuple[float, float],
        sample_observatory_id: UUID,
        sample_date_range: tuple[datetime, datetime],
        instrument_without_constraints: InstrumentSchema,
    ) -> None:
        """Should raise VisibilityConstraintsNotFoundException when instrument has no constraints"""

        ra, dec = sample_coordinates
        date_range_begin, date_range_end = sample_date_range

        service = VisibilityService(mock_db)

        with pytest.raises(VisibilityConstraintsNotFoundException):
            await service.get_ephemeris_visibility(
                ra=ra,
                dec=dec,
                instrument=instrument_without_constraints,
                observatory_id=sample_observatory_id,
                date_range_begin=date_range_begin,
                date_range_end=date_range_end,
                hi_res=True,
            )

    @pytest.mark.asyncio
    async def test_get_should_raise_instrument_not_found_when_instrument_does_not_exist(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_db: AsyncMock,
        sample_coordinates: tuple[float, float],
        sample_instrument_id: UUID,
    ) -> None:
        """Should raise InstrumentNotFoundException when instrument does not exist"""

        ra, dec = sample_coordinates
        mock_instrument_service = AsyncMock()
        mock_instrument_service.get.return_value = None
        monkeypatch.setattr(
            "across_server.routes.v1.tools.visibility_calculator.service.InstrumentService",
            MagicMock(return_value=mock_instrument_service),
        )

        service = VisibilityService(mock_db)

        with pytest.raises(InstrumentNotFoundException):
            await service.get(
                ra=ra,
                dec=dec,
                instrument_id=sample_instrument_id,
                date_range_begin=datetime.now(),
                date_range_end=datetime.now(),
                hi_res=False,
            )

    @pytest.mark.asyncio
    async def test_get_should_raise_http_exception_when_instrument_has_no_telescope(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_db: AsyncMock,
        sample_coordinates: tuple[float, float],
        sample_instrument_id: UUID,
    ) -> None:
        """Should raise HTTPException when instrument has no associated telescope"""

        ra, dec = sample_coordinates
        mock_instrument_model = MagicMock()
        mock_instrument_service = AsyncMock()
        mock_instrument_service.get.return_value = mock_instrument_model
        monkeypatch.setattr(
            "across_server.routes.v1.tools.visibility_calculator.service.InstrumentService",
            MagicMock(return_value=mock_instrument_service),
        )

        mock_instrument_schema = MagicMock()
        mock_instrument_schema.name = "Test Instrument"
        mock_instrument_schema.telescope = None
        monkeypatch.setattr(
            "across_server.routes.v1.tools.visibility_calculator.service.InstrumentSchema.from_orm",
            MagicMock(return_value=mock_instrument_schema),
        )

        service = VisibilityService(mock_db)

        with pytest.raises(HTTPException) as exc_info:
            await service.get(
                ra=ra,
                dec=dec,
                instrument_id=sample_instrument_id,
                date_range_begin=datetime.now(),
                date_range_end=datetime.now(),
                hi_res=False,
            )

        assert exc_info.value.status_code == 404
        assert "has no associated telescope" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_should_call_get_ephemeris_visibility_when_visibility_type_is_ephemeris(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_db: AsyncMock,
        sample_coordinates: tuple[float, float],
        sample_instrument_id: UUID,
        sample_telescope_id: str,
        sample_observatory_id: UUID,
    ) -> None:
        """Should call get_ephemeris_visibility when instrument visibility type is EPHEMERIS"""

        ra, dec = sample_coordinates
        mock_instrument_model = MagicMock()
        mock_instrument_service = AsyncMock()
        mock_instrument_service.get.return_value = mock_instrument_model
        monkeypatch.setattr(
            "across_server.routes.v1.tools.visibility_calculator.service.InstrumentService",
            MagicMock(return_value=mock_instrument_service),
        )

        mock_telescope = MagicMock()
        mock_telescope.observatory_id = sample_observatory_id
        mock_telescope_service = AsyncMock()
        mock_telescope_service.get.return_value = mock_telescope
        monkeypatch.setattr(
            "across_server.routes.v1.tools.visibility_calculator.service.TelescopeService",
            MagicMock(return_value=mock_telescope_service),
        )

        mock_instrument_schema = MagicMock()
        mock_instrument_schema.name = "Test Instrument"
        mock_instrument_schema.telescope = MagicMock()
        mock_instrument_schema.telescope.id = sample_telescope_id
        mock_instrument_schema.visibility_type = "ephemeris"
        monkeypatch.setattr(
            "across_server.routes.v1.tools.visibility_calculator.service.InstrumentSchema.from_orm",
            MagicMock(return_value=mock_instrument_schema),
        )

        mock_visibility = MagicMock()

        service = VisibilityService(mock_db)
        service.get_ephemeris_visibility = AsyncMock(return_value=mock_visibility)  # type: ignore

        result = await service.get(
            ra=ra,
            dec=dec,
            instrument_id=sample_instrument_id,
            date_range_begin=datetime.now(),
            date_range_end=datetime.now(),
            hi_res=False,
        )

        service.get_ephemeris_visibility.assert_called_once()
        assert result == mock_visibility

    @pytest.mark.asyncio
    async def test_get_should_raise_not_implemented_error_when_visibility_type_not_supported(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_db: AsyncMock,
        sample_coordinates: tuple[float, float],
        sample_instrument_id: UUID,
        sample_telescope_id: str,
        sample_observatory_id: UUID,
    ) -> None:
        """Should raise NotImplementedError when instrument visibility type is not supported"""

        ra, dec = sample_coordinates
        mock_instrument_model = MagicMock()
        mock_instrument_service = AsyncMock()
        mock_instrument_service.get.return_value = mock_instrument_model
        monkeypatch.setattr(
            "across_server.routes.v1.tools.visibility_calculator.service.InstrumentService",
            MagicMock(return_value=mock_instrument_service),
        )

        mock_telescope = MagicMock()
        mock_telescope.observatory_id = sample_observatory_id
        mock_telescope_service = AsyncMock()
        mock_telescope_service.get.return_value = mock_telescope
        monkeypatch.setattr(
            "across_server.routes.v1.tools.visibility_calculator.service.TelescopeService",
            MagicMock(return_value=mock_telescope_service),
        )

        mock_instrument_schema = MagicMock()
        mock_instrument_schema.name = "Test Instrument"
        mock_instrument_schema.telescope = MagicMock()
        mock_instrument_schema.telescope.id = sample_telescope_id
        mock_instrument_schema.visibility_type = "unsupported_type"
        monkeypatch.setattr(
            "across_server.routes.v1.tools.visibility_calculator.service.InstrumentSchema.from_orm",
            MagicMock(return_value=mock_instrument_schema),
        )

        service = VisibilityService(mock_db)

        with pytest.raises(VisibilityTypeNotImplementedException) as exc_info:
            await service.get(
                ra=ra,
                dec=dec,
                instrument_id=sample_instrument_id,
                date_range_begin=datetime.now(),
                date_range_end=datetime.now(),
                hi_res=False,
            )

        assert "Visibility type unsupported_type is not implemented" in str(
            exc_info.value
        )
