from enum import Enum


class InstrumentType(str, Enum):
    SPECTROSCOPIC_LOW_RES = "spectroscopic_low_res"
    SPECTROSCOPIC_HIGH_RES = "spectroscopic_high_res"
    PHOTOMETRIC = "photometric"
    CALORIMETER = "calorimeter"
    POLARIMETER = "polarimeter"
    SCINTILLATOR = "scintillator"
    XRAY_COUNTING_SPECTROMETER = "xray_counting_spectrometer"
