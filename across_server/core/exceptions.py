import logging
import uuid

from fastapi import HTTPException, status


class AcrossHTTPException(HTTPException):
    def __init__(self, status_code: int, message: str, log_data: dict):
        logging.error(
            message,
            log_data,
            exc_info=True,
        )

        super().__init__(status_code=status_code, detail=message)


class DuplicateEntityException(AcrossHTTPException):
    def __init__(self, entity_name: str, field_name: str, field_value: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"{entity_name} with {field_name} '{field_value}' already exists.",
            log_data={
                "entity": entity_name,
                f"{field_name}": field_value,
            },
        )


class NotFoundException(AcrossHTTPException):
    def __init__(self, entity_name: str, entity_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"{entity_name} not found.",
            log_data={
                f"{entity_name}": entity_id,
            },
        )
