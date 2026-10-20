import hashlib
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    System BaseSchema for generating new methods for our schemas taking advantage of the
    pydantic BaseModel.
    Methods
    -------
    generate_checksum() -> str:
        returns a string checksum string based on the encoded model json
    """

    # https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances
    model_config = ConfigDict(from_attributes=True)

    def generate_checksum(self) -> str:
        json_data = self.model_dump_json()
        return hashlib.sha512(json_data.encode()).hexdigest()


class IDNameSchema(BaseSchema):
    id: UUID
    name: str
    short_name: str | None


class PrefixMixin:
    """
    Mixin to allow Pydantic to flatten nested schemas
    during validation, given field names that share a prefix
    e.g. `pointing_position` -> `pointing_ra` and `pointing_dec`
    """

    def model_dump_with_prefix(
        self, prefix: str | None = None, data: dict = {}
    ) -> dict:
        data_with_prefixes = {}
        if prefix is not None:
            for key, value in data.items():
                data_with_prefixes[prefix + "_" + key] = value

        return data_with_prefixes
