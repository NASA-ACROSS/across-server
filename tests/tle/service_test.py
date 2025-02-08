from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.db.models import TLE
from across_server.routes.tle import schemas
from across_server.routes.tle.service import TLEService


class TestTLEService:
    @pytest.mark.asyncio
    @patch.object(TLEService, "exists", new_callable=AsyncMock)
    async def test_create_should_return_tle_when_successful(
        self, mock_exists: AsyncMock, mock_db: AsyncSession, mock_tle: schemas.TLECreate
    ) -> None:
        """Should return the tle when successful"""
        mock_exists.return_value = False
        service = TLEService(mock_db)
        tle = await service.create(mock_tle)
        assert isinstance(tle, TLE)

    @pytest.mark.asyncio
    async def test_tle_service_exists(mock_tle_service, mock_db):
        mock_tle_service = TLEService(mock_db)
        exists = await mock_tle_service.exists(norad_id=12345, epoch=datetime.now())
        assert exists is True

    @pytest.mark.asyncio
    @patch.object(TLEService, "exists", new_callable=AsyncMock)
    async def test_create_should_save_tle_to_database(
        self, mock_exists: AsyncMock, mock_db: AsyncSession, mock_tle: schemas.TLECreate
    ) -> None:
        """Should save the tle to the database when successful"""
        mock_exists.return_value = False
        service = TLEService(mock_db)
        await service.create(mock_tle)

        mock_db.commit.assert_called_once()  # type: ignore[attr-defined]
