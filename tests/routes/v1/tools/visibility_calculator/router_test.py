from unittest.mock import AsyncMock, MagicMock

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestVisibilityCalculatorRouter:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
    ) -> None:
        self.client = async_client
        self.endpoint = "/tools/visibility-calculator/windows/"

    @pytest.mark.asyncio
    async def test_get_should_return_404_when_instrument_does_not_exist(
        self,
        mock_instrument_service: AsyncMock,
        fake_visibility_read_params: dict,
    ) -> None:
        """Should return a 404 status when instrument does not exist"""
        mock_instrument_service.get.return_value = None

        res = await self.client.get(
            self.endpoint,
            params=fake_visibility_read_params,
        )
        assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_should_return_404_when_instrument_has_no_telescope(
        self,
        mock_instrument_service: AsyncMock,
        fake_instrument_schema_from_orm: MagicMock,
        fake_visibility_read_params: dict,
    ) -> None:
        """Should return a 404 status when instrument has no associated telescope"""
        fake_instrument_schema_from_orm.telescope = None
        mock_instrument_service.get.return_value = None

        res = await self.client.get(
            self.endpoint,
            params=fake_visibility_read_params,
        )
        assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
