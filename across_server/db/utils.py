from .models import Base as PostgresModel
from pydantic import BaseModel


def from_orm(
        schema: BaseModel, 
        model: PostgresModel, 
    ) -> BaseModel:
    """
    Returns the schema representation of a database model object
    utilizing the schema's `validate_from_database_model` method
    """
    return schema.model_config["return_schema"](**model.__dict__)