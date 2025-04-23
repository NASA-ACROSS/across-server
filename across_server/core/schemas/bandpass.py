from across.tools import (
    EnergyBandpass,
    FrequencyBandpass,
    WavelengthBandpass,
    convert_to_wave,
)
from across.tools import enums as tools_enums


class WavelengthBandpassCreate(WavelengthBandpass):
    pass


class FrequencyBandpassCreate(FrequencyBandpass):
    pass


class EnergyBandpassCreate(EnergyBandpass):
    pass


def bandpass_converter(
    bandpass: WavelengthBandpassCreate | FrequencyBandpassCreate | EnergyBandpassCreate,
) -> dict:
    """
    Converts the bandpass definition (in wavelength, frequency, or energy) to a standardized
    wavelength-based bandpass representation.

    Returns:
        dict: A dictionary containing:
            - "filter_name" (str): The name of the bandpass filter.
            - "min_wavelength" (float): Minimum wavelength of the bandpass.
            - "max_wavelength" (float): Maximum wavelength of the bandpass.
            - "peak_wavelength" (float): Peak wavelength of the bandpass.
    """
    unit = bandpass.unit
    if unit in tools_enums.WavelengthUnit:
        wavelength_bandpass = WavelengthBandpass(**bandpass.model_dump())

    elif unit in tools_enums.EnergyUnit:
        energy_bandpass = EnergyBandpass(**bandpass.model_dump())
        wavelength_bandpass = convert_to_wave(energy_bandpass)

    elif unit in tools_enums.FrequencyUnit:
        frequency_bandpass = FrequencyBandpass(**bandpass.model_dump())
        wavelength_bandpass = convert_to_wave(frequency_bandpass)

    return {
        "filter_name": wavelength_bandpass.filter_name,
        "min_wavelength": wavelength_bandpass.min,
        "max_wavelength": wavelength_bandpass.max,
        "peak_wavelength": wavelength_bandpass.peak_wavelength,
    }
