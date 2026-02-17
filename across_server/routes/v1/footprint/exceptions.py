import uuid

from ....core.exceptions import NotFoundException


class FootprintNotFoundException(NotFoundException):
    def __init__(self, instrument_id: uuid.UUID):
        super().__init__(entity_name="Instrument Footprint", entity_id=instrument_id)
