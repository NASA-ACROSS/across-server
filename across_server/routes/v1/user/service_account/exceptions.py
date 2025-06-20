import uuid

from .....core.exceptions import NotFoundException


class ServiceAccountNotFoundException(NotFoundException):
    def __init__(self, service_account_id: uuid.UUID):
        super().__init__(entity_name="ServiceAccount", entity_id=service_account_id)
