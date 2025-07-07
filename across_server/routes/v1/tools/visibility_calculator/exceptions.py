from uuid import UUID

from .....core.exceptions import NotFoundException


class VisibilityConstraintsNotFoundException(NotFoundException):
    def __init__(self, instrument_id: UUID):
        super().__init__(entity_name="Constraint", entity_id=instrument_id)
