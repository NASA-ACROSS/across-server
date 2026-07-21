import uuid

from ....core.exceptions import InvalidEntityException, NotFoundException


class ObservationRequestNotFoundException(NotFoundException):
    def __init__(self, observation_request_id: uuid.UUID):
        super().__init__(
            entity_name="ObservationRequest", entity_id=observation_request_id
        )


class InvalidObservationRequestReadParametersException(InvalidEntityException):
    def __init__(self, message: str):
        super().__init__(entity_name="ObservationRequestRead", message=message)


class InvalidObservationRequestCreateParametersException(InvalidEntityException):
    def __init__(self, message: str):
        super().__init__(entity_name="ObservationRequestCreate", message=message)
