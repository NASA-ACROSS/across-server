from pydantic import BaseModel

from ...core.date_utils import UTCDatetime
from .base import PrefixMixin


class DateRange(BaseModel, PrefixMixin):
    begin: UTCDatetime
    end: UTCDatetime


class NullableDateRange(DateRange):
    begin: UTCDatetime | None
    end: UTCDatetime | None
