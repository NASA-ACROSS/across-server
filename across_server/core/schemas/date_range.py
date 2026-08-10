from datetime import datetime, timezone
from typing import Self

from pydantic import BaseModel, model_validator

from ...core.date_utils import UTCDatetime
from .base import PrefixMixin


class DateRangeMixin(BaseModel, PrefixMixin):
    begin: UTCDatetime | None
    end: UTCDatetime | None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.begin is not None and self.end is not None and self.end <= self.begin:
            raise ValueError("End date must be after begin date")

        return self


class DateRange(DateRangeMixin):
    begin: UTCDatetime
    end: UTCDatetime


class NullableDateRange(DateRangeMixin):
    begin: UTCDatetime | None
    end: UTCDatetime | None


class NullableEndDateRange(DateRangeMixin):
    begin: UTCDatetime
    end: UTCDatetime | None


class NullableEndFutureDateRange(DateRangeMixin):
    begin: UTCDatetime
    end: UTCDatetime | None

    @model_validator(mode="after")
    def validate_future_date_range(self) -> Self:
        if self.begin <= datetime.now(timezone.utc).replace(tzinfo=None):
            raise ValueError("Begin date must be in the future")

        return self
