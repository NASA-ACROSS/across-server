import uuid

from .....core.exceptions import NotFoundException


class GroupInviteNotFoundException(NotFoundException):
    def __init__(self, id: uuid.UUID):
        super().__init__(entity_name="Group Invite", entity_id=id)
