from pydantic import BaseModel, field_validator
from datetime import datetime, timezone
from .base import PrefixMixin

class DateRange(BaseModel, PrefixMixin):
    begin: datetime
    end: datetime

    @field_validator('begin', 'end', mode='before')
    @classmethod
    def make_timezone_naive(cls, value: str) -> datetime:
        """
        Convert the datetime to UTC and remove timezone info 
        Timezone-naive datetime is needed for sqlalchemy
        """
        return datetime.fromisoformat(value).astimezone(timezone.utc).replace(tzinfo=None)