import hashlib
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.json_schema import SkipJsonSchema


def _flatten_dict(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, BaseModel):
            v = v.model_dump()  # convert before recursion

        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def _exclude_fields(data: Any, model: BaseModel) -> Any:
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            field = model.model_fields.get(key)
            if field and any([type(m) is SkipJsonSchema for m in field.metadata]):
                # Skip fields with SkipJsonSchema set to exclude
                continue

            attr = getattr(model, key, None)

            # Recurse into nested BaseModels
            if isinstance(attr, BaseModel):
                result[key] = _exclude_fields(value, attr)
            elif isinstance(attr, list) and attr and isinstance(attr[0], BaseModel):
                result[key] = [_exclude_fields(v, m) for v, m in zip(value, attr)]
            elif (
                isinstance(attr, dict)
                and attr
                and isinstance(next(iter(attr.values())), BaseModel)
            ):
                result[key] = {k: _exclude_fields(v, attr[k]) for k, v in value.items()}
            else:
                result[key] = value
        return result
    return data


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
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    def generate_checksum(self) -> str:
        json_data = self.model_dump_json()
        return hashlib.sha512(json_data.encode()).hexdigest()

    def model_dump(
        self, *args: Any, flatten: bool = False, **kwargs: Any
    ) -> dict[str, Any]:
        """Override the model_dump method to flatten the dictionary."""
        original_dump = super().model_dump(*args, **kwargs)
        if flatten:
            return _flatten_dict(original_dump)

        # Exclude fields with json_schema_extra set to exclude
        return _exclude_fields(original_dump, self)


class IDNameSchema(BaseSchema):
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
