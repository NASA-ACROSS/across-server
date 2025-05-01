from fastapi import status

from ...core.exceptions import AcrossHTTPException


class ObservationPointingPositionRequired(AcrossHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Pointing position is required.",
            log_data={
                "entity": "Observation",
                "message": "Pointing position is required.",
            },
        )
