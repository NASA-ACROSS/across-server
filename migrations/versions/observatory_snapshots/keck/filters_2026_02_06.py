import uuid

from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums

# NOTE: These bandwidths have been corrected to be accurate
#       for the conversion in across-tools
LRIS_U_BANDPASS = WavelengthBandpass(
    filter_name="u'",
    central_wavelength=3450,
    bandwidth=525 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_B_BANDPASS = WavelengthBandpass(
    filter_name="B",
    central_wavelength=4370,
    bandwidth=878 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_G_BANDPASS = WavelengthBandpass(
    filter_name="g",
    central_wavelength=4731,
    bandwidth=1082 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_V_BANDPASS = WavelengthBandpass(
    filter_name="V",
    central_wavelength=5437,
    bandwidth=922 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_R_BANDPASS = WavelengthBandpass(
    filter_name="R",
    central_wavelength=6417,
    bandwidth=1185 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_RS_BANDPASS = WavelengthBandpass(
    filter_name="Rs",
    central_wavelength=6809,
    bandwidth=1269 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_I_BANDPASS = WavelengthBandpass(
    filter_name="I",
    central_wavelength=7599,
    bandwidth=1225 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

LRIS_FILTERS: list[dict] = [
    {
        "id": uuid.UUID("9d5b016c-b7bd-4a75-939e-1f8193cf3a9c"),
        "name": "LRIS u'",
        "min_wavelength": LRIS_U_BANDPASS.min,
        "max_wavelength": LRIS_U_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("b91bc90a-0c00-48b1-8802-fc33d43fe14e"),
        "name": "LRIS B",
        "min_wavelength": LRIS_B_BANDPASS.min,
        "max_wavelength": LRIS_B_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("e3e4e09b-2d43-4b8a-9f04-68e6918362a1"),
        "name": "LRIS g",
        "min_wavelength": LRIS_G_BANDPASS.min,
        "max_wavelength": LRIS_G_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("aad1dfd3-de7b-4fef-ac9d-61858f7aef79"),
        "name": "LRIS V",
        "min_wavelength": LRIS_V_BANDPASS.min,
        "max_wavelength": LRIS_V_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("f360e9fc-c1b3-405f-bcb9-bb909a24c205"),
        "name": "LRIS R",
        "min_wavelength": LRIS_R_BANDPASS.min,
        "max_wavelength": LRIS_R_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("a656f058-c727-4132-96e7-2fb837d9d16f"),
        "name": "LRIS Rs",
        "min_wavelength": LRIS_RS_BANDPASS.min,
        "max_wavelength": LRIS_RS_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("60a58bf4-926d-4501-9e88-1fd5ef58df15"),
        "name": "LRIS I",
        "min_wavelength": LRIS_I_BANDPASS.min,
        "max_wavelength": LRIS_I_BANDPASS.max,
        "is_operational": True,
    },
]

NIRC2_Z_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 z",
    central_wavelength=1.0311,
    bandwidth=0.0481 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_Y_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Y",
    central_wavelength=1.018,
    bandwidth=0.0996 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_J_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 J",
    central_wavelength=1.248,
    bandwidth=0.163 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_H_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 H",
    central_wavelength=1.633,
    bandwidth=0.296 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_K_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 K",
    central_wavelength=2.196,
    bandwidth=0.336 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_KS_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Ks",
    central_wavelength=2.146,
    bandwidth=0.311 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_KP_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Kp",
    central_wavelength=2.124,
    bandwidth=0.351 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_LW_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Lw",
    central_wavelength=3.5197,
    bandwidth=1.3216 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_LP_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Lp",
    central_wavelength=3.776,
    bandwidth=0.7 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_MS_BANDPASS = WavelengthBandpass(
    filter_name="NIRC2 Ms",
    central_wavelength=4.67,
    bandwidth=0.241 / 2,
    unit=tools_enums.WavelengthUnit.MICRON,
)

NIRC2_FILTERS: list[dict] = [
    {
        "id": uuid.UUID("c171dcb9-0080-4183-8532-dd0c5ed628db"),
        "name": "NIRC2 z",
        "min_wavelength": NIRC2_Z_BANDPASS.min,
        "max_wavelength": NIRC2_Z_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("f56ba7ca-7a9c-49ef-b0ea-e239a7760793"),
        "name": "NIRC2 Y",
        "min_wavelength": NIRC2_Y_BANDPASS.min,
        "max_wavelength": NIRC2_Y_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("ff20163a-c57d-48f2-9b97-16f1b5c894cd"),
        "name": "NIRC2 J",
        "min_wavelength": NIRC2_J_BANDPASS.min,
        "max_wavelength": NIRC2_J_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("7936ed37-d95c-4a04-9aab-58e3482b918e"),
        "name": "NIRC2 H",
        "min_wavelength": NIRC2_H_BANDPASS.min,
        "max_wavelength": NIRC2_H_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("2eabb5fe-1ff8-4be9-8801-c3d62fbbe613"),
        "name": "NIRC2 K",
        "min_wavelength": NIRC2_K_BANDPASS.min,
        "max_wavelength": NIRC2_K_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("6ca77fa8-843d-4817-80d2-c67a615f6fd6"),
        "name": "NIRC2 Ks",
        "min_wavelength": NIRC2_KS_BANDPASS.min,
        "max_wavelength": NIRC2_KS_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("b5b890e6-8028-4d48-a76b-b6706d8ead56"),
        "name": "NIRC2 Kp",
        "min_wavelength": NIRC2_KP_BANDPASS.min,
        "max_wavelength": NIRC2_KP_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("eab2a043-aec7-45ff-8bad-970b0b6d09bf"),
        "name": "NIRC2 Lw",
        "min_wavelength": NIRC2_LW_BANDPASS.min,
        "max_wavelength": NIRC2_LW_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("78539254-82b3-4fb6-8587-f272ee6e569d"),
        "name": "NIRC2 Lp",
        "min_wavelength": NIRC2_LP_BANDPASS.min,
        "max_wavelength": NIRC2_LP_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("5d5b66e8-cc5e-4784-bda3-0962b24249c7"),
        "name": "NIRC2 Ms",
        "min_wavelength": NIRC2_MS_BANDPASS.min,
        "max_wavelength": NIRC2_MS_BANDPASS.max,
        "is_operational": True,
    },
]

DEIMOS_B_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS B Bandpass",
    central_wavelength=4416,
    bandwidth=373 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

DEIMOS_V_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS V Bandpass",
    central_wavelength=5452,
    bandwidth=628 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

DEIMOS_R_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS R Bandpass",
    central_wavelength=6487,
    bandwidth=810 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

DEIMOS_I_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS I Bandpass",
    central_wavelength=8390,
    bandwidth=1689 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

DEIMOS_Z_BANDPASS = WavelengthBandpass(
    filter_name="DEIMOS B Bandpass",
    central_wavelength=9085,
    bandwidth=969 / 2,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

DEIMOS_FILTERS: list[dict] = [
    {
        "id": uuid.UUID("703c0b55-08a0-4a99-b9e6-dc0b13c6e557"),
        "name": "DEIMOS B",
        "min_wavelength": DEIMOS_B_BANDPASS.min,
        "max_wavelength": DEIMOS_B_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("434fa960-db24-4271-9238-4010fe181c62"),
        "name": "DEIMOS V",
        "min_wavelength": DEIMOS_V_BANDPASS.min,
        "max_wavelength": DEIMOS_V_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("8282aedc-08e3-4bb4-8098-6b99a5e5de62"),
        "name": "DEIMOS R",
        "min_wavelength": DEIMOS_R_BANDPASS.min,
        "max_wavelength": DEIMOS_R_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("2e835669-c863-444a-9e99-cc7a13466c92"),
        "name": "DEIMOS I",
        "min_wavelength": DEIMOS_I_BANDPASS.min,
        "max_wavelength": DEIMOS_I_BANDPASS.max,
        "is_operational": True,
    },
    {
        "id": uuid.UUID("61acb4d3-d985-4f9f-a479-94d8797fc1a7"),
        "name": "DEIMOS Z",
        "min_wavelength": DEIMOS_Z_BANDPASS.min,
        "max_wavelength": DEIMOS_Z_BANDPASS.max,
        "is_operational": True,
    },
]
