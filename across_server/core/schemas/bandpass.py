from across.tools import (
    EnergyBandpass,
    FrequencyBandpass,
    WavelengthBandpass,
    convert_to_wave,
)
from across.tools import enums as tools_enums

from across_server.core.schemas.base import BaseSchema

from ..exceptions import UnproccessableEntityException


class BandpassSchema(BaseSchema):
    """
    Schema for representing a spectral bandpass filter.

    This class supports input in different spectral units (wavelength, frequency, or energy),
    and provides a method to normalize and convert any given input to a wavelength-based representation.

    Attributes:
        filter_name (str | None): Optional name identifier for the filter.
        min (float | None): Minimum value of the bandpass range.
        max (float | None): Maximum value of the bandpass range.
        central_wavelength (float | None): Central wavelength of the bandpass.
        bandwidth (float | None): Bandwidth of the filter in the corresponding unit.
        peak_wavelength (float | None): Wavelength at which the filter reaches its peak transmission.
        unit (Enum): The unit of the bandpass (can be wavelength, frequency, or energy).
    """

    filter_name: str | None = None
    min: float | None = None
    max: float | None = None
    central_wavelength: float | None = None
    bandwidth: float | None = None
    peak_wavelength: float | None = None
    unit: (
        tools_enums.WavelengthUnit | tools_enums.EnergyUnit | tools_enums.FrequencyUnit
    )

    def bandpass_converter(self) -> dict:
        """
        Converts the bandpass definition (in wavelength, frequency, or energy) to a standardized
        wavelength-based bandpass representation.

        Returns:
            dict: A dictionary containing:
                - "filter_name" (str): The name of the filter.
                - "central_wavelength" (float): Central wavelength of the bandpass.
                - "bandwidth" (float): Bandwidth in wavelength units.

        Raises:
            UnproccessableEntityException: If the conversion fails or an invalid unit is provided.
        """
        unit = self.unit
        if unit in tools_enums.WavelengthUnit:
            try:
                wavelength_bandpass = WavelengthBandpass(**self.model_dump())
            except Exception as e:
                raise UnproccessableEntityException(
                    entity_name="bandpass", description=f"{e}"
                )

        elif unit in tools_enums.EnergyUnit:
            try:
                energy_bandpass = EnergyBandpass(**self.model_dump())
                wavelength_bandpass = convert_to_wave(energy_bandpass)
            except Exception as e:
                raise UnproccessableEntityException(
                    entity_name="bandpass", description=f"{e}"
                )

        elif unit in tools_enums.FrequencyUnit:
            try:
                frequency_bandpass = FrequencyBandpass(**self.model_dump())
                wavelength_bandpass = convert_to_wave(frequency_bandpass)
            except Exception as e:
                raise UnproccessableEntityException(
                    entity_name="bandpass", description=f"{e}"
                )

        return {
            "filter_name": wavelength_bandpass.filter_name,
            "central_wavelength": wavelength_bandpass.central_wavelength,
            "bandwidth": wavelength_bandpass.bandwidth,
        }
