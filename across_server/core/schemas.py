from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, timezone
from typing import Optional
from ..db.enums import DepthUnit


class Permission(BaseModel):
    id: UUID
    name: str


class UnitValue(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    value: float | None
    unit: DepthUnit | None


class DateRange(BaseModel):
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


class Coordinate(BaseModel):
    ra: float | None = Field(ge=0.0, le=360.0)
    dec: float | None = Field(ge=-90.0, le=90.0)


class Bandpass(BaseModel):
    filter_name: Optional[str]
    central_wavelength: Optional[float]
    bandwidth: Optional[float]
