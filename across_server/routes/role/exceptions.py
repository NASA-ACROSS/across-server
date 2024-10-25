import uuid

from ...core.exceptions import NotFoundException


class RoleNotFoundException(NotFoundException):
    def __init__(self, id: uuid.UUID):
        super().__init__(entity_name="Role", entity_id=id)
