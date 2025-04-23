from across.tools import EnergyBandpass, FrequencyBandpass, WavelengthBandpass
from across.tools import enums as tools_enums

from across_server.core.schemas.bandpass import bandpass_converter


class TestBandpass:
    def test_converter_wavelength(self) -> None:
        schema = WavelengthBandpass(
            filter_name="test_filter",
            central_wavelength=500.0,
            bandwidth=100.0,
            unit=tools_enums.WavelengthUnit.NANOMETER,
        )
        result = bandpass_converter(schema)
        assert isinstance(result, WavelengthBandpass)

    def test_converter_energy(self) -> None:
        schema = EnergyBandpass(min=2.0, max=4.0, unit=tools_enums.EnergyUnit.keV)
        result = bandpass_converter(schema)
        assert isinstance(result, WavelengthBandpass)

    def test_converter_frequency(self) -> None:
        schema = FrequencyBandpass(
            min=3e14, max=6e14, unit=tools_enums.FrequencyUnit.Hz
        )
        result = bandpass_converter(schema)
        assert isinstance(result, WavelengthBandpass)
