from datetime import datetime

from fastapi import status

from ...core.exceptions import AcrossHTTPException


class DuplicateTLEException(AcrossHTTPException):
    def __init__(self, norad_id: int, epoch: datetime):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"TLE with norad_id {norad_id} and epoch {epoch} already exists.",
            log_data={
                "entity": "TLE",
                "norad_id": norad_id,
                "epoch": epoch,
            },
        )
