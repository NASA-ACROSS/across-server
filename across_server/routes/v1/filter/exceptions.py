import uuid

from ....core.exceptions import NotFoundException


class FilterNotFoundException(NotFoundException):
    def __init__(self, instrument_id: uuid.UUID):
        super().__init__(entity_name="Filter", entity_id=instrument_id)
