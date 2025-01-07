from typing import Optional

from pydantic import BaseModel


class Bandpass(BaseModel):
    filter_name: Optional[str]
    central_wavelength: Optional[float]
    bandwidth: Optional[float]
