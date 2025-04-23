from across.tools import (
    EnergyBandpass,
    FrequencyBandpass,
    WavelengthBandpass,
    convert_to_wave,
)


def bandpass_converter(
    bandpass: WavelengthBandpass | FrequencyBandpass | EnergyBandpass,
) -> WavelengthBandpass:
    """
    Converts the bandpass definition (in wavelength, frequency, or energy) to a standardized
    wavelength-based bandpass representation.

    Returns:
        WavelengthBandpass: The bandpass definition converted to a wavelength-based representation.
    """
    if isinstance(bandpass, WavelengthBandpass):
        return WavelengthBandpass(**bandpass.model_dump())

    return convert_to_wave(bandpass)
