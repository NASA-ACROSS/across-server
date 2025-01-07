import uuid

from ...core.exceptions import NotFoundException


class InstrumentNotFoundException(NotFoundException):
    def __init__(self, instrument_id: uuid.UUID):
        super().__init__(entity_name="Instrument", entity_id=instrument_id)
