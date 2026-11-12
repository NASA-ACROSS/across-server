from pydantic import BaseModel, Field

from .base import PrefixMixin


class ProperMotion(BaseModel, PrefixMixin):
    ra: float = Field()
    dec: float = Field()
    epoch: str = Field(max_length=16)
