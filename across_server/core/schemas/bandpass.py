from pydantic import BaseModel


class Bandpass(BaseModel):
    filter_name: str | None
    central_wavelength: float | None
    bandwidth: float | None
