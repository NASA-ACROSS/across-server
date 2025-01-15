from typing import Any

from .models import Base as PostgresModel


def from_orm(
    schema: Any,
    model: PostgresModel,
) -> Any:
    """
    Returns the schema representation of a database model object
    utilizing the schema's `return_schema`` attribute
    """
    return getattr(schema, "return_schema")(**model.__dict__)
