import uuid

from ...core.exceptions import DuplicateEntityException, NotFoundException


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: uuid.UUID):
        super().__init__(entity_name="User", entity_id=user_id)


class DuplicateUserException(DuplicateEntityException):
    def __init__(self, field_name: str, field_value: str):
        super().__init__(
            entity_name="User",
            field_name=field_name,
            field_value=field_value,
        )
