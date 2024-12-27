from pydantic import BaseModel, ConfigDict
from .base import PrefixMixin
from ..enums import DepthUnit


class UnitValue(BaseModel, PrefixMixin):
    model_config = ConfigDict(use_enum_values=True)

    value: float | None
    unit: DepthUnit | None