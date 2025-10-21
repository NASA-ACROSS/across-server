from datetime import datetime
from uuid import UUID

from fastapi import status

from .....core.exceptions import AcrossHTTPException
from ...observatory.schemas import ObservatoryEphemerisType


class EphemerisNotFound(AcrossHTTPException):
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


class EphemerisTypeNotFound(AcrossHTTPException):
    def __init__(self, observatory_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"No ephemeris types found for observatory {observatory_id}",
            log_data={
                "entity": "Ephemeris",
                "observatory_id": observatory_id,
            },
        )


class EphemerisCalculationNotFound(AcrossHTTPException):
    def __init__(
        self, observatory_id: UUID, ephem_types: list[ObservatoryEphemerisType]
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=(
                f"None of {ephem_types} could be used to calculate an ephemeris for observatory {observatory_id}. "
                "Please try again later. If this issue persists please contact support."
            ),
            log_data={
                "entity": "Ephemeris",
                "observatory_id": observatory_id,
                "ephemeris_types": ephem_types,
            },
        )
