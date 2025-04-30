import uuid

from fastapi import status

from ...core.exceptions import AcrossHTTPException, NotFoundException


class ScheduleNotFoundException(NotFoundException):
    def __init__(self, schedule_id: uuid.UUID):
        super().__init__(entity_name="Schedule", entity_id=schedule_id)


class DuplicateScheduleException(AcrossHTTPException):
    def __init__(self, schedule_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Duplicate Schedule detected with id {schedule_id} already exists.",
            log_data={"entity": "Schedule", "id": schedule_id},
        )


class InvalidScheduleInstrument(AcrossHTTPException):
    def __init__(self, instrument_id: uuid.UUID, telescope_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Invalid Instrument ID {instrument_id} in for telescope ID {telescope_id}.",
            log_data={"entity": "Schedule", "instrument_id": instrument_id},
        )
