import uuid

from ...core.exceptions import NotFoundException


class ObservatoryNotFoundException(NotFoundException):
    def __init__(self, observatory_id: uuid.UUID):
        super().__init__(entity_name="Observatory", entity_id=observatory_id)
