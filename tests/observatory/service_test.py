from uuid import uuid4

import pytest

from across_server.routes.observatory.exceptions import (
    ObservatoryNotFoundException,
)
from across_server.routes.observatory.service import ObservatoryService


class TestObservatoryService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self, mock_db, mock_scalar_one_or_none, mock_result
        ) -> None:
            """Should return False when the observatory does not exist"""
            mock_scalar_one_or_none.return_value = None
            mock_result.scalar_one_or_none = mock_scalar_one_or_none
            mock_db.execute.return_value = mock_result

            service = ObservatoryService(mock_db)
            with pytest.raises(ObservatoryNotFoundException):
                await service.get(uuid4())
