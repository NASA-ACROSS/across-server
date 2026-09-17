from pydantic import BaseModel

from ...core.date_utils import UTCDatetime
from .base import PrefixMixin


class NullableDateRange(BaseModel, PrefixMixin):
    begin: UTCDatetime | None
    end: UTCDatetime | None


class DateRange(NullableDateRange):
    begin: UTCDatetime
    end: UTCDatetime
