from pydantic import BaseModel


class Bandpass(BaseModel):
    filter_name: str | None
    peak_wavelength: float | None = None
    min_wavelength: float | None = None
    max_wavelength: float | None = None
