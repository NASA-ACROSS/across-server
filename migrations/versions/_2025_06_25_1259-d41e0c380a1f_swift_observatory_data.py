"""swift observatory data

Revision ID: d41e0c380a1f
Revises: d4208fedfabf
Create Date: 2025-06-25 12:59:16.210104

"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

from across.tools import EnergyBandpass, WavelengthBandpass, convert_to_wave
from across.tools import enums as tools_enums
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_06_18 as snapshot_models
from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from across_server.core.enums.observatory_type import ObservatoryType
from migrations.build_records import ssa_records
from migrations.db_util import arcmin_to_deg, circular_footprint, square_footprint

# revision identifiers, used by Alembic.
revision: str = "d41e0c380a1f"
down_revision: Union[str, None] = "d4208fedfabf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 23.6 arcmin x 23.6 arcmin square
SWIFT_XRT_footprint = circular_footprint(radius_deg=arcmin_to_deg(11.8))
# https://treasuremap.space/instrument_info?id=49
SWIFT_BAT_footprint = [
    [
        {"x": 57.65625, "y": 17.58278},
        {"x": 56.95312, "y": 19.47122},
        {"x": 56.25, "y": 21.38194},
        {"x": 55.54687, "y": 22.02431},
        {"x": 54.14062, "y": 24.62432},
        {"x": 53.4375, "y": 25.2826},
        {"x": 52.73438, "y": 25.94448},
        {"x": 52.03125, "y": 26.6101},
        {"x": 51.32813, "y": 27.27961},
        {"x": 50.625, "y": 27.95319},
        {"x": 49.92187, "y": 28.63099},
        {"x": 46.40625, "y": 30.69159},
        {"x": 45.70312, "y": 31.38817},
        {"x": 42.89062, "y": 32.79717},
        {"x": 42.1875, "y": 33.51006},
        {"x": 40.07812, "y": 34.22887},
        {"x": 37.26562, "y": 35.68533},
        {"x": 35.15625, "y": 36.42357},
        {"x": 28.82812, "y": 38.68219},
        {"x": 23.20312, "y": 40.22818},
        {"x": 18.28125, "y": 41.0145},
        {"x": 13.35938, "y": 41.81031},
        {"x": 11.95312, "y": 41.81031},
        {"x": 3.57143, "y": 42.60981},
        {"x": 2.14286, "y": 42.60981},
        {"x": 0.71429, "y": 42.60981},
        {"x": -0.7142900000000054, "y": 42.60981},
        {"x": -2.1428599999999847, "y": 42.60981},
        {"x": -3.5714300000000208, "y": 42.60981},
        {"x": -11.953120000000013, "y": 41.81031},
        {"x": -13.359379999999987, "y": 41.81031},
        {"x": -18.28125, "y": 41.0145},
        {"x": -23.203120000000013, "y": 40.22818},
        {"x": -28.828120000000013, "y": 38.68219},
        {"x": -35.15625, "y": 36.42357},
        {"x": -37.26562000000001, "y": 35.68533},
        {"x": -40.07812999999999, "y": 34.22887},
        {"x": -42.1875, "y": 33.51006},
        {"x": -42.89062999999999, "y": 32.79717},
        {"x": -45.70312000000001, "y": 31.38817},
        {"x": -46.40625, "y": 30.69159},
        {"x": -49.92187999999999, "y": 28.63099},
        {"x": -50.625, "y": 27.95319},
        {"x": -51.32812000000001, "y": 27.27961},
        {"x": -52.03125, "y": 26.6101},
        {"x": -52.73437999999999, "y": 25.94448},
        {"x": -53.4375, "y": 25.2826},
        {"x": -54.14062000000001, "y": 24.62432},
        {"x": -55.54687999999999, "y": 22.02431},
        {"x": -56.25, "y": 21.38194},
        {"x": -56.95312000000001, "y": 19.47122},
        {"x": -57.65625, "y": 17.58278},
        {"x": -58.35937999999999, "y": 14.47751},
        {"x": -59.0625, "y": 11.41516},
        {"x": -59.0625, "y": 10.19992},
        {"x": -59.0625, "y": 8.9893},
        {"x": -59.0625, "y": 7.78271},
        {"x": -59.0625, "y": 6.57959},
        {"x": -61.17187999999999, "y": 2.38802},
        {"x": -60.46875, "y": 0.59684},
        {"x": -59.76562000000001, "y": -1.19375},
        {"x": -59.0625, "y": -2.98551},
        {"x": -58.35937999999999, "y": -3.58332},
        {"x": -57.65625, "y": -5.37938},
        {"x": -56.95312000000001, "y": -7.18076},
        {"x": -56.25, "y": -8.9893},
        {"x": -55.54687999999999, "y": -9.59407},
        {"x": -54.84375, "y": -11.41516},
        {"x": -54.14062000000001, "y": -13.24801},
        {"x": -53.4375, "y": -13.86195},
        {"x": -52.73437999999999, "y": -15.71386},
        {"x": -52.03125, "y": -17.58278},
        {"x": -51.32812000000001, "y": -18.20996},
        {"x": -50.625, "y": -20.10551},
        {"x": -49.92187999999999, "y": -20.74238},
        {"x": -49.21875, "y": -22.66961},
        {"x": -48.51562000000001, "y": -23.31796},
        {"x": -47.8125, "y": -23.96948},
        {"x": -45.70312000000001, "y": -27.27961},
        {"x": -45.0, "y": -27.95319},
        {"x": -44.29687999999999, "y": -28.63099},
        {"x": -43.59375, "y": -29.3132},
        {"x": -42.89062999999999, "y": -30.0},
        {"x": -40.07812999999999, "y": -31.38817},
        {"x": -39.375, "y": -32.08995},
        {"x": -38.67187999999999, "y": -32.79717},
        {"x": -35.85937999999999, "y": -34.22887},
        {"x": -35.15625, "y": -34.95387},
        {"x": -33.04687999999999, "y": -35.68533},
        {"x": -30.9375, "y": -36.42357},
        {"x": -30.234379999999987, "y": -37.1689},
        {"x": -28.125, "y": -37.92165},
        {"x": -26.015629999999987, "y": -38.68219},
        {"x": -24.609379999999987, "y": -38.68219},
        {"x": -22.5, "y": -39.45089},
        {"x": -20.390620000000013, "y": -40.22818},
        {"x": -18.984379999999987, "y": -40.22818},
        {"x": -15.46875, "y": -41.0145},
        {"x": -11.953120000000013, "y": -41.81031},
        {"x": -10.546879999999987, "y": -41.81031},
        {"x": -3.5714300000000208, "y": -42.60981},
        {"x": -2.1428599999999847, "y": -42.60981},
        {"x": -0.7142900000000054, "y": -42.60981},
        {"x": 0.71429, "y": -42.60981},
        {"x": 2.14286, "y": -42.60981},
        {"x": 3.57143, "y": -42.60981},
        {"x": 10.54688, "y": -41.81031},
        {"x": 11.95312, "y": -41.81031},
        {"x": 15.46875, "y": -41.0145},
        {"x": 18.98438, "y": -40.22818},
        {"x": 20.39062, "y": -40.22818},
        {"x": 22.5, "y": -39.45089},
        {"x": 24.60938, "y": -38.68219},
        {"x": 26.01562, "y": -38.68219},
        {"x": 28.125, "y": -37.92165},
        {"x": 30.23438, "y": -37.1689},
        {"x": 30.9375, "y": -36.42357},
        {"x": 33.04687, "y": -35.68533},
        {"x": 35.15625, "y": -34.95387},
        {"x": 35.85938, "y": -34.22887},
        {"x": 38.67187, "y": -32.79717},
        {"x": 39.375, "y": -32.08995},
        {"x": 40.07812, "y": -31.38817},
        {"x": 42.89062, "y": -30.0},
        {"x": 43.59375, "y": -29.3132},
        {"x": 44.29688, "y": -28.63099},
        {"x": 45.0, "y": -27.95319},
        {"x": 45.70312, "y": -27.27961},
        {"x": 47.8125, "y": -23.96948},
        {"x": 48.51562, "y": -23.31796},
        {"x": 49.21875, "y": -22.66961},
        {"x": 49.92187, "y": -20.74238},
        {"x": 50.625, "y": -20.10551},
        {"x": 51.32813, "y": -18.20996},
        {"x": 52.03125, "y": -17.58278},
        {"x": 52.73438, "y": -15.71386},
        {"x": 53.4375, "y": -13.86195},
        {"x": 54.14062, "y": -13.24801},
        {"x": 54.84375, "y": -11.41516},
        {"x": 55.54687, "y": -9.59407},
        {"x": 56.25, "y": -8.9893},
        {"x": 56.95312, "y": -7.18076},
        {"x": 57.65625, "y": -5.37938},
        {"x": 58.35937, "y": -3.58332},
        {"x": 59.0625, "y": -2.98551},
        {"x": 59.76562, "y": -1.19375},
        {"x": 60.46875, "y": 0.59684},
        {"x": 61.17187, "y": 2.38802},
        {"x": 59.0625, "y": 6.57959},
        {"x": 59.0625, "y": 7.78271},
        {"x": 59.0625, "y": 8.9893},
        {"x": 59.0625, "y": 10.19992},
        {"x": 59.0625, "y": 11.41516},
        {"x": 58.35937, "y": 14.47751},
        {"x": 57.65625, "y": 17.58278},
    ]
]
# 17 arcmin x 17 arcmin square
SWIFT_UVOT_footprint = square_footprint(length_deg=arcmin_to_deg(17.0))

SWIFT_XRT_ENERGY_BANDPASS = EnergyBandpass(
    min=0.3,
    max=10.0,
    unit=tools_enums.EnergyUnit.keV,
)
SWIFT_XRT_WAVELENGTH_BANDPASS = convert_to_wave(SWIFT_XRT_ENERGY_BANDPASS)

SWIFT_BAT_ENERGY_BANDPASS = EnergyBandpass(
    min=15.0,
    max=150.0,
    unit=tools_enums.EnergyUnit.keV,
)
SWIFT_BAT_WAVELENGTH_BANDPASS = convert_to_wave(SWIFT_BAT_ENERGY_BANDPASS)

SWIFT_UVOT_UVW2_WAVELENGTH_BANDPASS = WavelengthBandpass(
    min=160.0,
    max=350.0,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
SWIFT_UVOT_UVM2_WAVELENGTH_BANDPASS = WavelengthBandpass(
    min=170.0,
    max=300.0,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
SWIFT_UVOT_UVW1_WAVELENGTH_BANDPASS = WavelengthBandpass(
    min=160.0,
    max=470.0,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
SWIFT_UVOT_U_WAVELENGTH_BANDPASS = WavelengthBandpass(
    min=300.0,
    max=400.0,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
SWIFT_UVOT_V_WAVELENGTH_BANDPASS = WavelengthBandpass(
    min=400.0,
    max=500.0,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
SWIFT_UVOT_B_WAVELENGTH_BANDPASS = WavelengthBandpass(
    min=500.0,
    max=600.0,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)
SWIFT_UVOT_WHITE_WAVELENGTH_BANDPASS = WavelengthBandpass(
    min=160.0,
    max=800.0,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)


OBSERVATORY: dict = {
    "id": uuid.UUID("d5faadca-c0bb-4bb8-b4e4-75149b435ae8"),
    "name": "Neil Gehrels Swift Observatory",
    "short_name": "Swift",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://swift.gsfc.nasa.gov/about_swift/",
    "telescopes": [
        {
            "id": uuid.UUID("c4249d8b-f5aa-43fb-9c46-aaa9b503c446"),
            "name": "Burst Alert Telescope",
            "short_name": "Swift_BAT",
            "is_operational": True,
            "reference_url": "https://swift.gsfc.nasa.gov/about_swift/bat_desc.html",
            "instruments": [
                {
                    "id": uuid.UUID("dbe7c3e5-384f-4a04-a6f8-d7b4625e06d2"),
                    "name": "Burst Alert Telescope",
                    "short_name": "Swift_BAT",
                    "type": InstrumentType.CODED_APERTURE_IMAGER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": SWIFT_BAT_footprint,
                    "reference_url": "https://swift.gsfc.nasa.gov/about_swift/bat_desc.html",
                    "filters": [
                        {
                            "id": uuid.UUID("363520b6-11d4-401e-ab55-f28361576e8d"),
                            "name": "Swift BAT",
                            "min_wavelength": SWIFT_BAT_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": SWIFT_BAT_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        }
                    ],
                }
            ],
        },
        {
            "id": uuid.UUID("4994a365-428f-40ce-92ae-64393b8b565a"),
            "name": "X-ray Telescope",
            "short_name": "Swift_XRT",
            "is_operational": True,
            "reference_url": "https://swift.gsfc.nasa.gov/about_swift/xrt_desc.html",
            "instruments": [
                {
                    "id": uuid.UUID("77b85f25-3ce6-4351-a77a-1d793492be88"),
                    "name": "X-ray Telescope",
                    "short_name": "Swift_XRT",
                    "type": InstrumentType.XRAY_IMAGING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": SWIFT_XRT_footprint,
                    "reference_url": "https://swift.gsfc.nasa.gov/about_swift/xrt_desc.html",
                    "filters": [
                        {
                            "id": uuid.UUID("aae9d2b6-83c8-42c0-922d-04276c22e7dd"),
                            "name": "Swift XRT",
                            "min_wavelength": SWIFT_XRT_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": SWIFT_XRT_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        }
                    ],
                },
            ],
        },
        {
            "id": uuid.UUID("a17fb486-a194-4354-8c4c-f7582fd790bc"),
            "name": "UV/Optical Telescope",
            "short_name": "Swift_UVOT",
            "is_operational": True,
            "reference_url": "https://swift.gsfc.nasa.gov/about_swift/uvot_desc.html",
            "instruments": [
                {
                    "id": uuid.UUID("1c074192-f6d5-465d-844e-85a0010b2d87"),
                    "name": "UV/Optical Telescope",
                    "short_name": "Swift_UVOT",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": SWIFT_UVOT_footprint,
                    "reference_url": "https://swift.gsfc.nasa.gov/about_swift/uvot_desc.html",
                    "filters": [
                        {
                            "id": uuid.UUID("078c5918-7f32-4a2d-baf0-f89c61c6f6bf"),
                            "name": "Swift UVOT UVW2",
                            "min_wavelength": SWIFT_UVOT_UVW2_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": SWIFT_UVOT_UVW2_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("d4d4bc72-38ca-4055-abe5-984ff46f2df0"),
                            "name": "Swift UVOT UVM2",
                            "min_wavelength": SWIFT_UVOT_UVM2_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": SWIFT_UVOT_UVM2_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("22c411fe-a230-404f-812b-436decc7747f"),
                            "name": "Swift UVOT UVW1",
                            "min_wavelength": SWIFT_UVOT_UVW1_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": SWIFT_UVOT_UVW1_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("bff880f2-b72e-428a-a6bb-7a03fd22c3cb"),
                            "name": "Swift UVOT U",
                            "min_wavelength": SWIFT_UVOT_U_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": SWIFT_UVOT_U_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("ee053989-a8b6-44b8-8dfb-5f0d92e2365d"),
                            "name": "Swift UVOT B",
                            "min_wavelength": SWIFT_UVOT_B_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": SWIFT_UVOT_B_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("279eb39b-b5ac-4fee-a9af-58af8d350148"),
                            "name": "Swift UVOT V",
                            "min_wavelength": SWIFT_UVOT_V_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": SWIFT_UVOT_V_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("06beb8f8-5350-4062-9b73-720ba5b75ab5"),
                            "name": "Swift UVOT White",
                            "min_wavelength": SWIFT_UVOT_WHITE_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": SWIFT_UVOT_WHITE_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("00e78af7-383b-4fdb-bd7d-a74b3925bc8b"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("018fa55f-53a1-4b39-9bd4-6e8202019e11"),
                "norad_id": 28485,
                "norad_satellite_name": "Swift",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("3f86950f-5acf-479a-bdda-1c5c4e201876"),
        "name": "Neil Gehrels Swift Observatory",
        "short_name": "Swift",
        "group_admin": {
            "id": uuid.UUID("a9ef386a-bfaf-4f99-89be-f607f26cbb2d"),
            "name": "Swift Group Admin",
        },
    },
}


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    records = ssa_records.build(session, OBSERVATORY, snapshot_models)

    session.add_all(records)
    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    ssa_records.delete(session, OBSERVATORY, snapshot_models)

    session.commit()
