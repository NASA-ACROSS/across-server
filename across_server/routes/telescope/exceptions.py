import uuid

from ...core.exceptions import NotFoundException


class TelescopeNotFoundException(NotFoundException):
    def __init__(self, telescope_id: uuid.UUID):
        super().__init__(entity_name="Telescope", entity_id=telescope_id)
