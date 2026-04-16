import uuid

from ....core.exceptions import NotFoundException


class BrokerEventNotFoundException(NotFoundException):
    def __init__(self, broker_event_id: uuid.UUID):
        super().__init__(entity_name="BrokerEvent", entity_id=broker_event_id)
