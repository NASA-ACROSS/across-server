from enum import Enum


class ObservationType(str, Enum):
    IMAGING = "imaging"
    TIMING = "timing"
    SPECTROSCOPY = "spectroscopy"