import uuid

from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums

OM_UVW2_BANDPASS = WavelengthBandpass(
    filter_name="OM UVW2",
    central_wavelength=212,
    bandwidth=50,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
OM_UVM2_BANDPASS = WavelengthBandpass(
    filter_name="OM UVM2",
    central_wavelength=231,
    bandwidth=48,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
OM_UVW1_BANDPASS = WavelengthBandpass(
    filter_name="OM UVW1",
    central_wavelength=291,
    bandwidth=83,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
OM_U_BANDPASS = WavelengthBandpass(
    filter_name="OM U",
    central_wavelength=344,
    bandwidth=84,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
OM_B_BANDPASS = WavelengthBandpass(
    filter_name="OM B",
    central_wavelength=450,
    bandwidth=105,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
OM_V_BANDPASS = WavelengthBandpass(
    filter_name="OM V",
    central_wavelength=543,
    bandwidth=70,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
OM_WHITE_BANDPASS = WavelengthBandpass(
    filter_name="OM White",
    central_wavelength=406,
    bandwidth=347,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)

OM_FILTERS: list[dict] = [
    {
        "id": uuid.UUID("c0dd7859-c54c-444b-bb83-dd352f262685"),
        "name": "XMM-Newton OM UVW2",
        "min_wavelength": OM_UVW2_BANDPASS.min,
        "max_wavelength": OM_UVW2_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("4c5b0687-dfa4-495e-a6da-e6b2091c69a9"),
        "name": "XMM-Newton OM UVM2",
        "min_wavelength": OM_UVM2_BANDPASS.min,
        "max_wavelength": OM_UVM2_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("51872a86-a6fd-46ab-b540-090449192efe"),
        "name": "XMM-Newton OM UVW1",
        "min_wavelength": OM_UVW1_BANDPASS.min,
        "max_wavelength": OM_UVW1_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("b4ef5eb9-9689-477c-82bf-eff9e17ea4e1"),
        "name": "XMM-Newton OM U",
        "min_wavelength": OM_U_BANDPASS.min,
        "max_wavelength": OM_U_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("cfdcaf7e-980d-4b10-8cef-9333ee71b7dc"),
        "name": "XMM-Newton OM B",
        "min_wavelength": OM_B_BANDPASS.min,
        "max_wavelength": OM_B_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("5623b15e-b2e7-4dd5-869c-d51211ef75e9"),
        "name": "XMM-Newton OM V",
        "min_wavelength": OM_V_BANDPASS.min,
        "max_wavelength": OM_V_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("be3c6758-1f41-4c0c-9a9c-c42ccbf440ca"),
        "name": "XMM-Newton OM White",
        "min_wavelength": OM_WHITE_BANDPASS.min,
        "max_wavelength": OM_WHITE_BANDPASS.max,
        "is_operational": True,
    },
]
