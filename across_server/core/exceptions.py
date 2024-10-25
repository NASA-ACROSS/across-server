import logging
import uuid

from fastapi import HTTPException, status


class DuplicateEntityException(HTTPException):
    def __init__(self, entity_name: str, field_name: str, field_value: str):
        message = f"{entity_name} with {field_name} '{field_value}' already exists."

        logging.error(
            message,
            {
                "entity": entity_name,
                f"{field_name}": field_value,
            },
            exc_info=True,
        )

        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class NotFoundException(HTTPException):
    def __init__(self, entity_name: str, entity_id: uuid.UUID):
        message = f"{entity_name} not found."

        logging.error(
            message,
            {
                f"{entity_name}": entity_id,
            },
            exc_info=True,
        )

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )
