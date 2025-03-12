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


class IDNameSchema(BaseModel):
    id: UUID
    name: str


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


class CoordinateConverterMixin:
    """
    Mixin to allow Pydantic to nest fields for
    Coordinate schema during validation
    """

    @staticmethod
    def coordinate_converter(values: dict) -> dict:
        coordinates: dict = {}
        for key, value in values.items():
            if key.endswith("_ra") or key.endswith("_dec"):
                coord_name = key.split("_")[0] + "_position"
                coordinates.setdefault(coord_name, {}).update(
                    {"ra" if "_ra" in key else "dec": value}
                )
        if bool(coordinates):
            values.update(coordinates)
        return values


class DateRangeConverterMixin:
    """
    Mixin to allow Pydantic to nest fields for
    DateRange schema during validation
    """

    @staticmethod
    def date_range_converter(values: dict, name: str) -> dict:
        date_range: dict = {}
        for key, value in values.items():
            if key.endswith("_begin") or key.endswith("_end"):
                field_name = key.split("_")[-1]
                date_range[field_name] = value
        if bool(date_range):
            values.update({name: date_range})
        return values


class UnitValueConverterMixin:
    """
    Mixin to allow Pydantic to nest fields for
    UnitValue schema during validation
    """

    @staticmethod
    def unit_value_converter(values: dict, name: str) -> dict:
        unit_value: dict = {}
        for key, value in values.items():
            if key.endswith("_unit") or key.endswith("_value"):
                field_name = key.split("_")[-1]
                unit_value[field_name] = value
        if bool(unit_value):
            values.update({name: unit_value})
        return values


class BandpassConverterMixin:
    """
    Mixin to allow Pydantic to nest fields for
    Bandpass schema during validation
    """

    @staticmethod
    def bandpass_converter(values: dict, name: str) -> dict:
        bandpass: dict = {}
        for key, value in values.items():
            if key in ["filter_name", "central_wavelength", "bandwidth"]:
                bandpass[key] = value
        if bool(bandpass):
            values.update({name: bandpass})
        return values
