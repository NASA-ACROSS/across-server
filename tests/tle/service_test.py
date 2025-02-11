from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.db.models import TLE
from across_server.routes.tle import schemas
from across_server.routes.tle.service import TLEService


class TestTLEService:
    @pytest.mark.asyncio
    async def test_get_should_return_tle_when_get_successful(
        self, mock_tle_service: TLEService, mock_db: AsyncSession
    ) -> None:
        """
        The test verifies that the returned object is an instance of TLE class.
        """
        tle = await mock_tle_service.get(norad_id=12345, epoch=datetime.now())
        assert isinstance(tle, TLE)
        tle_schema = schemas.TLE.model_validate(tle)
        assert abs((tle_schema.epoch - datetime.now()).days) <= 1

    @pytest.mark.asyncio
    async def test_get_should_return_none_if_not_found(
        self, mock_result: AsyncMock, mock_db: AsyncSession
    ) -> None:
        """
        Test that TLEService returns None when no TLE object is found.
        """
        mock_result.scalar_one_or_none.return_value = None
        service = TLEService(mock_db)
        tle = await service.get(norad_id=34235, epoch=datetime.now())
        assert tle is None

    @pytest.mark.asyncio
    async def test_should_return_tle_when_create_successful(
        self, mock_result: AsyncMock, mock_db: AsyncSession, mock_tle: schemas.TLECreate
    ) -> None:
        """
        Test that TLE creation returns a TLE object when creation is successful.
        """
        mock_result.scalar_one_or_none.return_value = None
        service = TLEService(mock_db)
        tle = await service.create(mock_tle)
        assert isinstance(tle, TLE)

    @pytest.mark.asyncio
    async def test_should_return_true_when_tle_exists(mock_tle_service, mock_db):
        """
        Test that TLEService returns true when a TLE exists for given parameters.
        """

        mock_tle_service = TLEService(mock_db)
        exists = await mock_tle_service.exists(norad_id=12345, epoch=datetime.now())
        assert exists is True

    @pytest.mark.asyncio
    async def test_create_should_save_tle_to_database(
        self, mock_result: AsyncMock, mock_db: AsyncSession, mock_tle: schemas.TLECreate
    ) -> None:
        """
        Test that create method saves TLE to database.
        """
        mock_result.scalar_one_or_none.return_value = None
        service = TLEService(mock_db)
        await service.create(mock_tle)

        mock_db.commit.assert_called_once()  # type: ignore[attr-defined]
