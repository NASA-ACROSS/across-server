from uuid import UUID

from .....core.exceptions import NotFoundException, NotImplementedException


class VisibilityConstraintsNotFoundException(NotFoundException):
    def __init__(self, instrument_id: UUID):
        super().__init__(entity_name="Constraint", entity_id=instrument_id)


class VisibilityTypeNotImplementedException(NotImplementedException):
    def __init__(self, message: str):
        super().__init__(message)
