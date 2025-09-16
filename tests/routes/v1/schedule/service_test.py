from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from across_server.db.models import Instrument as InstrumentModel
from across_server.db.models import Schedule as ScheduleModel
from across_server.routes.v1.schedule.exceptions import (
    DuplicateScheduleException,
    ScheduleInstrumentNotFoundException,
    ScheduleNotFoundException,
)
from across_server.routes.v1.schedule.schemas import (
    ScheduleCreate,
    ScheduleCreateMany,
    ScheduleRead,
)
from across_server.routes.v1.schedule.service import ScheduleService


class TestScheduleService:
    class TestCreate:
        @pytest.mark.asyncio
        async def test_should_raise_duplicate_exception(
            self,
            mock_db: AsyncMock,
            schedule_create_example: ScheduleCreate,
            instrument_model_example: InstrumentModel,
            mock_result: AsyncMock,
            fake_schedule_data: ScheduleModel,
        ) -> None:
            """Should raise duplicate schedule"""
            # sets the checksum query to a value so it raises
            mock_result.scalars.return_value.all.return_value = [
                fake_schedule_data,
            ]
            mock_db.execute.return_value = mock_result
            service = ScheduleService(mock_db)

            with pytest.raises(DuplicateScheduleException):
                await service.create(
                    schedule_create_example,
                    instruments=[instrument_model_example],
                    created_by_id=uuid4(),
                )

        @pytest.mark.asyncio
        async def test_should_raise_invalid_instrument(
            self,
            mock_db: AsyncMock,
            schedule_create_example: ScheduleCreate,
            mock_scalar_one_or_none: MagicMock,
            instrument_model_example: InstrumentModel,
            mock_result: AsyncMock,
        ) -> None:
            """Should raise invalid instrument"""
            # sets the checksum query to a value so it raises
            mock_scalar_one_or_none.return_value = None
            mock_result.scalar_one_or_none = mock_scalar_one_or_none
            mock_db.execute.return_value = mock_result
            service = ScheduleService(mock_db)

            instrument_model_example.id = uuid4()

            with pytest.raises(ScheduleInstrumentNotFoundException):
                await service.create(
                    schedule_create_example,
                    instruments=[instrument_model_example],
                    created_by_id=uuid4(),
                )

        @pytest.mark.asyncio
        async def test_should_save_schedule_to_database(
            self,
            mock_db: AsyncMock,
            schedule_create_example: ScheduleCreate,
            instrument_model_example: InstrumentModel,
            mock_result: AsyncMock,
        ) -> None:
            """Should save the schedule to the database when successful"""
            # sets the checksum query to None so it creates
            mock_result.scalars.return_value.all.return_value = []
            mock_db.execute.return_value = mock_result
            service = ScheduleService(mock_db)
            await service.create(
                schedule_create_example,
                instruments=[instrument_model_example],
                created_by_id=uuid4(),
            )

            mock_db.commit.assert_called_once()

    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_not_found_exception_when_does_not_exist(
            self,
            mock_db: AsyncMock,
            mock_scalar_one_or_none: MagicMock,
            mock_result: AsyncMock,
        ) -> None:
            """Should raise ScheduleNotFoundException when the schedule does not exist"""
            mock_scalar_one_or_none.return_value = None
            mock_result.scalar_one_or_none = mock_scalar_one_or_none
            mock_db.execute.return_value = mock_result

            service = ScheduleService(mock_db)
            with pytest.raises(ScheduleNotFoundException):
                await service.get(uuid4())

    class TestGetMany:
        @pytest.mark.asyncio
        async def test_should_return_list_when_successful(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_schedule_data: ScheduleModel,
        ) -> None:
            """Should return a list of Schedule models when get_many is successful"""
            mock_result.tuples.return_value.all.return_value = [
                fake_schedule_data,
                fake_schedule_data,
            ]
            service = ScheduleService(mock_db)
            params = ScheduleRead()
            schedules = await service.get_many(params)
            assert isinstance(schedules, list)

    class TestGetHistory:
        @pytest.mark.asyncio
        async def test_should_return_list_when_successful(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_schedule_data: ScheduleModel,
        ) -> None:
            """Should return a list of Schedule models when get_history is successful"""
            mock_result.tuples.return_value.all.return_value = [
                fake_schedule_data,
                fake_schedule_data,
            ]
            service = ScheduleService(mock_db)
            params = ScheduleRead()
            schedules = await service.get_history(params)
            assert isinstance(schedules, list)

    class TestCreateMany:
        @pytest.mark.asyncio
        async def test_should_not_raise_duplicate_exception(
            self,
            mock_db: AsyncMock,
            schedule_create_many_example: ScheduleCreateMany,
            instrument_model_example: InstrumentModel,
            mock_result: AsyncMock,
            fake_schedule_data: ScheduleModel,
        ) -> None:
            """Should not raise duplicate schedule"""
            # sets the checksum query to a value
            mock_result.scalars.return_value.all.return_value = [
                fake_schedule_data,
                fake_schedule_data,
            ]
            mock_db.execute.return_value = mock_result
            service = ScheduleService(mock_db)

            await service.create_many(
                schedule_create_many_example,
                instruments=[instrument_model_example],
                created_by_id=uuid4(),
            )
            # test passes if no exception is raised and commit() is called
            mock_db.commit.assert_called_once()

        @pytest.mark.asyncio
        async def test_should_raise_invalid_instrument(
            self,
            mock_db: AsyncMock,
            schedule_create_many_example: ScheduleCreateMany,
            mock_scalar_one_or_none: MagicMock,
            instrument_model_example: InstrumentModel,
            mock_result: AsyncMock,
        ) -> None:
            """Should raise invalid instrument exception"""
            mock_scalar_one_or_none.return_value = None
            mock_result.scalar_one_or_none = mock_scalar_one_or_none
            mock_db.execute.return_value = mock_result
            service = ScheduleService(mock_db)

            instrument_model_example.id = uuid4()

            with pytest.raises(ScheduleInstrumentNotFoundException):
                await service.create_many(
                    schedule_create_many_example,
                    instruments=[instrument_model_example],
                    created_by_id=uuid4(),
                )
