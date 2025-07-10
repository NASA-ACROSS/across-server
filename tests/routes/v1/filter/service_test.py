from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.routes.v1.filter.exceptions import FilterNotFoundException
from across_server.routes.v1.filter.schemas import FilterRead
from across_server.routes.v1.filter.service import FilterService


class TestFilterService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self, mock_db: AsyncMock, mock_result: AsyncMock
        ) -> None:
            """Should raise a not found exception when the filter does not exist"""
            mock_result.scalar_one_or_none.return_value = None

            service = FilterService(mock_db)
            with pytest.raises(FilterNotFoundException):
                await service.get(uuid4())

        class TestGetMany:
            @pytest.mark.asyncio
            async def test_should_return_empty_list_when_nothing_matches_params(
                self, mock_db: AsyncMock, mock_result: AsyncMock
            ) -> None:
                """Should return False when the filter does not exist"""
                mock_result.scalars.all.return_value = []

                service = FilterService(mock_db)
                params = FilterRead()
                values = await service.get_many(params)
                assert len(values) == 0
