import uuid

from fastapi import status

from ...core.exceptions import AcrossHTTPException, NotFoundException


class ObservationNotFoundException(NotFoundException):
    def __init__(self, observation_id: uuid.UUID):
        super().__init__(entity_name="Observation", entity_id=observation_id)


class InvalidObservationReadParametersException(AcrossHTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            log_data={},
        )
