from pydantic import BaseModel
from typing import Optional

class Bandpass(BaseModel):
    filter_name: Optional[str]
    central_wavelength: Optional[float]
    bandwidth: Optional[float]