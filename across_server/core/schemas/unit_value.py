from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from .base import PrefixMixin

T = TypeVar("T")


class UnitValue(BaseModel, PrefixMixin, Generic[T]):
    model_config = ConfigDict(use_enum_values=True)

    value: float
    unit: T
