from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from across_server.db.models import Schedule as ScheduleModel
from across_server.routes.schedule.exceptions import (
    DuplicateScheduleException,
    ScheduleNotFoundException,
)
from across_server.routes.schedule.schemas import ScheduleCreate
from across_server.routes.schedule.service import ScheduleService


class TestScheduleService:
    class TestCreate:
        @pytest.mark.asyncio
        async def test_should_raise_duplicate_exception(
            self,
            mock_db: AsyncMock,
            schedule_create_example: ScheduleCreate,
            mock_scalar_one_or_none: MagicMock,
            mock_result: AsyncMock,
            mock_schedule_data: ScheduleModel,
        ) -> None:
            """Should raise duplicate schedule"""
            # sets the checksum query to a value so it raises
            mock_scalar_one_or_none.return_value = mock_schedule_data
            mock_result.scalar_one_or_none = mock_scalar_one_or_none
            mock_db.execute.return_value = mock_result
            service = ScheduleService(mock_db)

            with pytest.raises(DuplicateScheduleException):
                await service.create(schedule_create_example, created_by_id=uuid4())

        @pytest.mark.asyncio
        async def test_should_save_service_account_to_database(
            self,
            mock_db: AsyncMock,
            schedule_create_example: ScheduleCreate,
            mock_scalar_one_or_none: MagicMock,
            mock_result: AsyncMock,
        ) -> None:
            """Should save the service_account to the database when successful"""
            # sets the checksum query to None so it creates
            mock_scalar_one_or_none.return_value = None
            mock_result.scalar_one_or_none = mock_scalar_one_or_none
            mock_db.execute.return_value = mock_result
            service = ScheduleService(mock_db)
            await service.create(schedule_create_example, created_by_id=uuid4())

            mock_db.commit.assert_called_once()

    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            mock_result: AsyncMock,
        ) -> None:
            """Should return False when the service account does not exist"""
            mock_scalar_one_or_none.return_value = None
            mock_result.scalar_one_or_none = mock_scalar_one_or_none
            mock_db.execute.return_value = mock_result

            service = ScheduleService(mock_db)
            with pytest.raises(ScheduleNotFoundException):
                await service.get(uuid4())
