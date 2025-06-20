import uuid

from .....core.exceptions import NotFoundException


class GroupRoleNotFoundException(NotFoundException):
    def __init__(self, id: uuid.UUID):
        super().__init__(entity_name="Group Role", entity_id=id)
