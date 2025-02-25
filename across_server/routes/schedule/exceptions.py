import uuid

from fastapi import status

from ...core.exceptions import AcrossHTTPException, NotFoundException


class ScheduleNotFoundException(NotFoundException):
    def __init__(self, schedule_id: uuid.UUID):
        super().__init__(entity_name="Schedule", entity_id=schedule_id)


class DuplicateScheduleException(AcrossHTTPException):
    def __init__(self, schedule_id: uuid.UUID, checksum: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Duplicate Schedule detected with id {schedule_id} and checksum {checksum} already exists.",
            log_data={
                "entity": "Schedule",
                "id": schedule_id,
                "checksum": checksum,
            },
        )
