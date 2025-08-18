"""XMM-Newton observatory migration

Revision ID: 826bca5cbc49
Revises: d5c4e2fc57bc
Create Date: 2025-08-12 13:36:03.356225

"""

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
from migrations.util.footprint_util import (
    arcmin_to_deg,
    project_footprint,
    rectangle_footprint,
    square_footprint,
)

# revision identifiers, used by Alembic.
revision: str = "826bca5cbc49"
down_revision: Union[str, None] = "d5c4e2fc57bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


EPIC_ENERGY_BANDPASS = EnergyBandpass(
    filter_name="XMM-Newton EPIC",
    min=0.3,
    max=12.0,
    unit=tools_enums.EnergyUnit.keV,
)
EPIC_BANDPASS = convert_to_wave(EPIC_ENERGY_BANDPASS)
"""
EPIC MOS footprint is made up of 7 10.9'x10.9' CCDs
arranged in three columns (2, 3, 2), as shown below:

          ----- 10.9
    ----- |   | -----
    |   | ----- |   | 10.9
    ----- |   | -----
    ----- ----- -----
    |   | ----- |   |
    ----- |   | -----
          -----
In the code below we will translate the same square ccd footprint 7 times:
I assume that my reference coordinate is at 0,0. For example, for the top right ccd
    dx=(5.45+5.45)
        5.45' is the distance from the center of the middle CCD to the right edge
        5.45' is the distance from the left edge to the center of the right CCD
    dy=5.45
        5.45' is the distance from the center of the middle CCD to the center of the right CCD
"""
epic_mos_ccd = square_footprint(length_deg=arcmin_to_deg(10.9))
EPIC_MOS_FOOTPRINT = [
    # top left: dx=-(5.45+5.45), dy=(5.45)
    project_footprint(
        epic_mos_ccd,
        ra_deg=-arcmin_to_deg(5.45 + 5.45),
        dec_deg=arcmin_to_deg(5.45),
    )[0],
    # bottom left: dx=-(5.45+5.45), dy=-(5.45)
    project_footprint(
        epic_mos_ccd, ra_deg=-arcmin_to_deg(5.45 + 5.45), dec_deg=-arcmin_to_deg(5.45)
    )[0],
    # top middle: dx=0, dy=(5.45+5.45)
    project_footprint(epic_mos_ccd, ra_deg=0, dec_deg=arcmin_to_deg(5.45 + 5.45))[0],
    # middle middle: dx=0, dy=0
    project_footprint(epic_mos_ccd, ra_deg=0, dec_deg=0)[0],
    # bottom middle: dx=0, dy=-(5.45+5.45)
    project_footprint(epic_mos_ccd, ra_deg=0, dec_deg=-arcmin_to_deg(5.45 + 5.45))[0],
    # top right: dx=(5.45+5.45), dy=(5.45)
    project_footprint(
        epic_mos_ccd, ra_deg=arcmin_to_deg(5.45 + 5.45), dec_deg=arcmin_to_deg(5.45)
    )[0],
    # bottom right: dx=(5.45+5.45), dy=-(5.45)
    project_footprint(
        epic_mos_ccd,
        ra_deg=arcmin_to_deg(5.45 + 5.45),
        dec_deg=-arcmin_to_deg(5.45),
    )[0],
]

"""
EPIC pn is made up of 12 13.6'x4.4' rectangular CCDS,
arranged in a rectangular pattern (2 rows of 6 columns).
There is a slight overlap between each CCD, but we can approximate
the overall footprint as a rectangle with width (4.4*6 = 26.4')
and height (13.6*2=27.2').
EPIC pn shares the same bandpass as EPIC MOS.
"""
EPIC_PN_FOOTPRINT = rectangle_footprint(
    width_deg=arcmin_to_deg(26.4),
    height_deg=arcmin_to_deg(27.2),
)

"""
The Reflection Grating Spectrometer (RGS) is a high-resolution
spectrograph on XMM-Newton that shares a FOV with EPIC MOS
"""
RGS_ENERGY_BANDPASS = EnergyBandpass(
    filter_name="XMM-Newton RGS",
    min=0.35,
    max=2.5,
    unit=tools_enums.EnergyUnit.keV,
)
RGS_BANDPASS = convert_to_wave(RGS_ENERGY_BANDPASS)

"""
The Optical Monitor is a UV-optical imager with similar filters
to Swift UVOT and a 17'x17' square field of view.
"""
OM_FOOTPRINT = square_footprint(length_deg=arcmin_to_deg(17))

# From https://heasarc.gsfc.nasa.gov/docs/xmm/uhb/omfilters.html
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

OBSERVATORY: dict = {
    "id": uuid.UUID("639a2cf5-0b68-449b-846f-d117fd771c8d"),
    "name": "X-ray Multi-Mirror Mission",
    "short_name": "XMM-Newton",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/xmm/xmmgof.html",
    "telescopes": [
        # There are actually 3 telescopes on XMM-Newton, but each have
        # duplicate instruments (e.g., two have EPIC-MOS), and given
        # that the instruments observe simultaneously, I'm just treating
        # the observatory as having one telescope with one of each instrument
        {
            "id": uuid.UUID("f2ae30ec-cd64-41b1-a951-4da29aa9f4ab"),
            "name": "X-ray Multi-Mirror Mission",
            "short_name": "XMM-Newton",
            "is_operational": True,
            "reference_url": "https://heasarc.gsfc.nasa.gov/docs/xmm/xmmgof.html",
            "instruments": [
                {
                    "id": uuid.UUID("ab55be45-9796-40da-8125-e512f446ac96"),
                    "name": "European Photon Imaging Camera - MOS",
                    "short_name": "EPIC-MOS",
                    "type": InstrumentType.XRAY_IMAGING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": EPIC_MOS_FOOTPRINT,
                    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/xmm/uhb/epic.html",
                    "filters": [
                        {
                            "id": uuid.UUID("4b2b3dcd-6c94-4d99-88ee-be0c825fc17e"),
                            "name": "XMM-Newton EPIC-MOS",
                            "min_wavelength": EPIC_BANDPASS.min,
                            "max_wavelength": EPIC_BANDPASS.max,
                            "is_operational": True,
                        }
                    ],
                },
                {
                    "id": uuid.UUID("b9c82f10-1292-462b-85b3-1c1c2292806c"),
                    "name": "European Photon Imaging Camera - pn",
                    "short_name": "EPIC-PN",
                    "type": InstrumentType.XRAY_IMAGING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": EPIC_PN_FOOTPRINT,
                    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/xmm/uhb/epic.html",
                    "filters": [
                        {
                            "id": uuid.UUID("37feb38f-03fc-41b6-987b-4e9994096a0f"),
                            "name": "XMM-Newton EPIC-pn",
                            "min_wavelength": EPIC_BANDPASS.min,
                            "max_wavelength": EPIC_BANDPASS.max,
                            "is_operational": True,
                        }
                    ],
                },
                {
                    "id": uuid.UUID("eb40e1c6-6c03-4474-9462-73d273efa3ac"),
                    "name": "Reflection Grating Spectrometer",
                    "short_name": "RGS",
                    "type": InstrumentType.XRAY_COUNTING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": EPIC_MOS_FOOTPRINT,
                    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/xmm/uhb/rgs.html",
                    "filters": [
                        {
                            "id": uuid.UUID("98f3fd5b-9847-426e-b221-70cc296a4783"),
                            "name": "XMM-Newton RGS",
                            "min_wavelength": RGS_BANDPASS.min,
                            "max_wavelength": RGS_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("e523b7de-8ea0-46eb-ba42-dff6f336130c"),
                    "name": "Optical Monitor",
                    "short_name": "OM",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": OM_FOOTPRINT,
                    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/xmm/uhb/om.html",
                    "filters": [
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
                    ],
                },
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("7b3d8839-5e71-4c33-a143-38b34ca0029b"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("5e5e5d25-4c01-46c7-802a-6587acd2c6ce"),
                "norad_id": 25989,
                "norad_satellite_name": "XMM",
            },
        },
        {
            "id": uuid.UUID("fbf2e434-edb4-4371-9417-c7905dcf2113"),
            "ephemeris_type": EphemerisType.JPL.value,
            "priority": 2,
            "parameters": {
                "id": uuid.UUID("df3c593b-5779-43ce-a20b-8d0b4b77e962"),
                "naif_id": -125989,
            },
        },
    ],
    "group": {
        "id": uuid.UUID("8940930c-7d7e-4f39-bb34-ba6c8ca8bcba"),
        "name": "X-ray Multi-Mirror Mission",
        "short_name": "XMM-Newton",
        "group_admin": {
            "id": uuid.UUID("3c3b96fd-d1af-47db-a991-d28240038f0f"),
            "name": "XMM-Newton Group Admin",
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
