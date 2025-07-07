from datetime import datetime
from uuid import UUID

from fastapi import status

from .....core.exceptions import AcrossHTTPException


class EphemerisOutsideOperationalRangeException(AcrossHTTPException):
    def __init__(
        self,
        date_range_begin: datetime,
        date_range_end: datetime,
        observatory_id: UUID,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Date range {date_range_begin} to {date_range_end} is outside the operational range of the observatory {observatory_id}",
            log_data={
                "entity": "Ephemeris",
                "observatory_id": observatory_id,
                "date_range": (date_range_begin, date_range_end),
            },
        )


class NoEphemerisTypesFoundException(AcrossHTTPException):
    def __init__(self, observatory_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"No ephemeris types found for observatory {observatory_id}",
            log_data={
                "entity": "Ephemeris",
                "observatory_id": observatory_id,
            },
        )
