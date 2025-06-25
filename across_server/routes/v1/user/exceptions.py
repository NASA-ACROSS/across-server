import uuid

from fastapi import status

from ....core.exceptions import (
    AcrossHTTPException,
    DuplicateEntityException,
    NotFoundException,
)


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


class UserEmailNotFoundException(AcrossHTTPException):
    def __init__(self, user_email: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"User with email {user_email} not found.",
            log_data={
                "entity": "User",
                "user_email": user_email,
            },
        )
