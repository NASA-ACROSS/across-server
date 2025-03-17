from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.routes.observatory.exceptions import (
    ObservatoryNotFoundException,
)
from across_server.routes.observatory.schemas import ObservatoryRead
from across_server.routes.observatory.service import ObservatoryService


class TestObservatoryService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should raise a not found exception when the observatory does not exist"""
            mock_result.scalar_one_or_none.return_value = None

            service = ObservatoryService(mock_db)
            with pytest.raises(ObservatoryNotFoundException):
                await service.get(uuid4())

        class TestGetMany:
            @pytest.mark.asyncio
            async def test_should_return_empty_list_when_nothing_matches_params(
                self, mock_db: AsyncMock, mock_result: AsyncMock
            ) -> None:
                """Should return an empty list when there are no matching observatories"""
                mock_result.scalars.all.return_value = []
                # mock_db.execute.return_value = mock_result

                service = ObservatoryService(mock_db)
                params = ObservatoryRead()
                values = await service.get_many(params)
                assert len(values) == 0
