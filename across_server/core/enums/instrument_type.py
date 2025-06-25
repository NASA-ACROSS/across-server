from enum import Enum


class InstrumentType(str, Enum):
    SPECTROSCOPIC_LOW_RES = "spectroscopic_low_res"
    SPECTROSCOPIC_HIGH_RES = "spectroscopic_high_res"
    PHOTOMETRIC = "photometric"
    CALORIMETER = "calorimeter"
    POLARIMETER = "polarimeter"
    SCINTILLATOR = "scintillator"
    XRAY_COUNTING_SPECTROMETER = "xray_counting_spectrometer"
    CODED_APERTURE_IMAGER = "coded_aperture_imager"
    XRAY_IMAGING_SPECTROMETER = "xray_imaging_spectrometer"
