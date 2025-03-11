from uuid import uuid4

import pytest

from across_server.routes.telescope.exceptions import (
    TelescopeNotFoundException,
)
from across_server.routes.telescope.service import TelescopeService


class TestTelescopeService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self, mock_db, mock_result
        ) -> None:
            """Should return False when the telescope does not exist"""
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result

            service = TelescopeService(mock_db)
            with pytest.raises(TelescopeNotFoundException):
                await service.get(uuid4())
