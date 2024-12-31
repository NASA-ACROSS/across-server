from pydantic import BaseModel, field_validator
from datetime import datetime
from .base import PrefixMixin
from across_server.core.date_utils import convert_to_utc

class DateRange(BaseModel, PrefixMixin):
    begin: datetime
    end: datetime

    @field_validator('begin', 'end', mode='before')
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        """
        Convert the datetime to UTC and remove timezone info 
        Timezone-naive datetime is needed for sqlalchemy
        """
        return convert_to_utc(value)