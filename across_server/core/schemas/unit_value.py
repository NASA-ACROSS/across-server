from pydantic import BaseModel, ConfigDict

from ..enums import DepthUnit
from .base import PrefixMixin


class UnitValue(BaseModel, PrefixMixin):
    model_config = ConfigDict(use_enum_values=True)

    value: float | None
    unit: DepthUnit | None
