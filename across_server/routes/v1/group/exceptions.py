import uuid

from ....core.exceptions import NotFoundException


class GroupNotFoundException(NotFoundException):
    def __init__(self, id: uuid.UUID):
        super().__init__(entity_name="Group", entity_id=id)
