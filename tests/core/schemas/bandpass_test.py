import numpy as np
from across.tools import enums as tools_enums

from across_server.core.schemas.bandpass import (
    EnergyBandpassCreate,
    FrequencyBandpassCreate,
    WavelengthBandpassCreate,
    bandpass_converter,
)


class TestBandpass:
    def test_converter_wavelength(self) -> None:
        schema = WavelengthBandpassCreate(
            filter_name="test_filter",
            central_wavelength=500.0,
            bandwidth=100.0,
            unit=tools_enums.WavelengthUnit.NANOMETER,
        )
        result = bandpass_converter(schema)
        assert result["filter_name"] == "test_filter"
        assert np.isclose(result["min_wavelength"], 4000.0)
        assert np.isclose(result["max_wavelength"], 6000.0)

    def test_converter_energy(self) -> None:
        schema = EnergyBandpassCreate(min=2.0, max=4.0, unit=tools_enums.EnergyUnit.keV)
        result = bandpass_converter(schema)
        assert "min_wavelength" in result
        assert "max_wavelength" in result

    def test_converter_frequency(self) -> None:
        schema = FrequencyBandpassCreate(
            min=3e14, max=6e14, unit=tools_enums.FrequencyUnit.Hz
        )
        result = bandpass_converter(schema)
        assert "min_wavelength" in result
        assert "max_wavelength" in result
