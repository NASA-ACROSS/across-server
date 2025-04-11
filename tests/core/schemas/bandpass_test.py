import numpy as np
import pytest
from across.tools import enums as tools_enums

from across_server.core.exceptions import UnproccessableEntityException
from across_server.core.schemas import Bandpass


class TestBandpass:
    def test_converter_wavelength(self) -> None:
        schema = Bandpass(
            filter_name="test_filter",
            central_wavelength=500.0,
            bandwidth=100.0,
            unit=tools_enums.WavelengthUnit.NANOMETER,
        )
        result = schema.bandpass_converter()
        assert result["filter_name"] == "test_filter"
        assert np.isclose(result["central_wavelength"], 5000.0)
        assert np.isclose(result["bandwidth"], 1000.0)

    def test_converter_energy(self) -> None:
        schema = Bandpass(min=2.0, max=4.0, unit=tools_enums.EnergyUnit.keV)
        result = schema.bandpass_converter()
        assert "central_wavelength" in result
        assert "bandwidth" in result

    def test_converter_frequency(self) -> None:
        schema = Bandpass(min=3e14, max=6e14, unit=tools_enums.FrequencyUnit.Hz)
        result = schema.bandpass_converter()
        assert "central_wavelength" in result
        assert "bandwidth" in result

    def test_converter_missing_min_max_energy(self) -> None:
        schema = Bandpass(unit=tools_enums.EnergyUnit.keV)
        with pytest.raises(UnproccessableEntityException):
            schema.bandpass_converter()

    def test_converter_missing_min_max_frequency(self) -> None:
        schema = Bandpass(unit=tools_enums.FrequencyUnit.Hz)
        with pytest.raises(UnproccessableEntityException):
            schema.bandpass_converter()

    def test_converter_missing_wavelength(self) -> None:
        schema = Bandpass(unit=tools_enums.WavelengthUnit.ANGSTROM)
        with pytest.raises(UnproccessableEntityException):
            schema.bandpass_converter()
