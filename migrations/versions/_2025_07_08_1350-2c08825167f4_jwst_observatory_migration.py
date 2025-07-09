"""jwst_observatory_migration

Revision ID: 2c08825167f4
Revises: d41e0c380a1f
Create Date: 2025-07-08 13:50:51.430172

"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_06_18 as snapshot_models
from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from across_server.core.enums.observatory_type import ObservatoryType
from migrations.build_records import ssa_records
from migrations.db_util import (
    arcsec_to_degree,
    rectangle_footprint,
    rotate_footprint,
    square_footprint,
    translate_footprint,
)
from migrations.versions.filters.jwst import filters as JWST_FILTERS

# revision identifiers, used by Alembic.
revision: str = "2c08825167f4"
down_revision: Union[str, None] = "d41e0c380a1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

"""
MIRI Footprint is composed of 5 modules, but the true imaging detector is a rectangle
of 74"x113" and rotated about 4.7degrees
"""
MIRI_FOOTPRINT = rotate_footprint(
    rectangle_footprint(
        width_deg=arcsec_to_degree(74.0), height_deg=arcsec_to_degree(113.0)
    ),
    4.7,
)

"""
NIRISS Footprint is a square footprint 133"x133"
"""
NIRISS_FOOTPRINT = square_footprint(arcsec_to_degree(133))

"""
NIRCam Footprint is two uniform modules approx 132"x132" separated by 44"
Each module has 4 ccds that are 64"x64"
   The ccds have 5" chip gaps in the x direction, and 4" in the y direction
This can be approximated by creating 2 132"x132" square footprints and shifting one
   -22" in the x direction and shifting the other 22" in the x direction

     64  5  64    44    64  5  64
    ----- -----        ----- -----
    |   | |   |        |   | |   | 64
    ----- -----        ----- -----
                                   4
    ----- -----        ----- -----
    |   | |   |        |   | |   | 64
    ----- -----        ----- -----
In the code below we will translate the same square ccd footprint 8 times:
I assume that my reference coordinate is at 0,0. For example, for the top right ccd
    dx=(22+64+5+32)
        22" is half the center separation distance of 44" in the x direction
        64" is the distance of middle left ccd
        5" is the chip gap of the x direction for the module
        32" is half the distance of the ccd, corresponding to the center of the desired ccd
    dy=(2+32)
        2" is half the distance of the chip gap in the y direction
        32" is half the distance of the ccd, corresponding to the center of the desired ccd
"""

nircam_ccd = square_footprint(length_deg=arcsec_to_degree(64))
NIRCAM_FOOTPRINT = [
    # The left module
    # top left: dx=-(22+64+5+32), dy=(2+32)
    translate_footprint(
        nircam_ccd, dx=-arcsec_to_degree(22 + 64 + 5 + 32), dy=arcsec_to_degree(2 + 32)
    )[0],
    # top right: dx=-(22+32), dy=(2+32)
    translate_footprint(
        nircam_ccd, dx=-arcsec_to_degree(22 + 32), dy=arcsec_to_degree(2 + 32)
    )[0],
    # bottom left: dx=-(22+32), dy=-(2+32)
    translate_footprint(
        nircam_ccd, dx=-arcsec_to_degree(22 + 32), dy=-arcsec_to_degree(2 + 32)
    )[0],
    # bottom right: dx=-(22+64+5+32), dy=-(2+32)
    translate_footprint(
        nircam_ccd, dx=-arcsec_to_degree(22 + 64 + 5 + 32), dy=-arcsec_to_degree(2 + 32)
    )[0],
    # The right module
    # top left: dx=(22+32). dy=(2+32)
    translate_footprint(
        nircam_ccd, dx=arcsec_to_degree(22 + 32), dy=arcsec_to_degree(2 + 32)
    )[0],
    # top right: dx=(22+64+5+32), dy=(2+32)
    translate_footprint(
        nircam_ccd, dx=arcsec_to_degree(22 + 64 + 5 + 32), dy=arcsec_to_degree(2 + 32)
    )[0],
    # bottom left: dx=(22+64+5+32), dy=-(2+32)
    translate_footprint(
        nircam_ccd, dx=arcsec_to_degree(22 + 64 + 5 + 32), dy=-arcsec_to_degree(2 + 32)
    )[0],
    # bottom right: dx=(22+32), dy=-(2+32)
    translate_footprint(
        nircam_ccd, dx=arcsec_to_degree(22 + 32), dy=-arcsec_to_degree(2 + 32)
    )[0],
]

"""
NIRSpec has 4 ccd's that are 1.5'x 1.5' (or 90 arcsec)
the chip gaps have 24" in the x direction and 37" in the y direction
The entire ensemble is also rotated 138.5 degrees in the counter-clockwise direction

     90    24    90
    -----      -----
    |   |      |   | 90
    -----      -----
                     37
    -----      -----
    |   |      |   | 90
    -----      -----
In the code below we will translate the same square ccd footprint 4 times:
I assume that my reference coordinate is at 0,0. For example, for the top right ccd
    dx=(12+45)
        12" is half the distance of chip gap (24") in the x direction
        45" is half the distance of the ccd, corresponding to the center of the desired ccd
    dy=(18.5+45)
        18.5" is half the distance of the chip gap (37) in the y direction
        45" is half the distance of the ccd, corresponding to the center of the desired ccd
"""
nirspec_ccd = square_footprint(arcsec_to_degree(90))
nirspec_footprint_non_rotated = [
    # Top left: dx=-(12+45) dy=(18.5+45)
    translate_footprint(
        nirspec_ccd, dx=-arcsec_to_degree(12 + 45), dy=arcsec_to_degree(18.5 + 45)
    )[0],
    # Top right: dx=(12+45) dy=(18.5+45)
    translate_footprint(
        nirspec_ccd, dx=arcsec_to_degree(12 + 45), dy=arcsec_to_degree(18.5 + 45)
    )[0],
    # Bottom right: dx=(12+45) dy=-(18.5+45)
    translate_footprint(
        nirspec_ccd, dx=arcsec_to_degree(12 + 45), dy=-arcsec_to_degree(18.5 + 45)
    )[0],
    # Bottom left: dx=(12+45) dy=-(18.5+45)
    translate_footprint(
        nirspec_ccd, dx=-arcsec_to_degree(12 + 45), dy=-arcsec_to_degree(18.5 + 45)
    )[0],
]
NIRSPEC_FOOTPRINT = rotate_footprint(nirspec_footprint_non_rotated, 138.5)

OBSERVATORY: dict = {
    "id": uuid.UUID("fefe0ddc-07af-4312-b3a8-051c4e646619"),
    "name": "James Webb Space Telescope",
    "short_name": "JWST",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://jwst-docs.stsci.edu/",
    "telescopes": [
        {
            "id": uuid.UUID("225ad468-585f-4f5e-8b64-09a4adfa1b7d"),
            "name": "James Webb Space Telescope",
            "short_name": "JWST",
            "reference_url": "https://jwst-docs.stsci.edu/",
            "instruments": [
                {
                    "id": uuid.UUID("d21c66bc-7173-454e-8f67-69df1b43590d"),
                    "name": "Mid-Infrared Instrument",
                    "short_name": "JWST_MIRI",
                    "reference_url": "https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": MIRI_FOOTPRINT,
                    "filters": JWST_FILTERS["JWST_MIRI"],
                },
                {
                    "id": uuid.UUID("9899d36c-9e07-4927-8295-04c4ced70f1a"),
                    "name": "Near-Infrared Camera",
                    "short_name": "JWST_NIRCAM",
                    "reference_url": "https://jwst-docs.stsci.edu/jwst-near-infrared-camera",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": NIRCAM_FOOTPRINT,
                    "filters": JWST_FILTERS["JWST_NIRCAM"],
                },
                {
                    "id": uuid.UUID("905bd0aa-6be2-43a1-b1d3-bb8df1632ac8"),
                    "name": "Near-Infrared Imager and Slitless Spectrograph",
                    "short_name": "JWST_NIRISS",
                    "reference_url": "https://jwst-docs.stsci.edu/jwst-near-infrared-imager-and-slitless-spectrograph",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": NIRISS_FOOTPRINT,
                    "filters": JWST_FILTERS["JWST_NIRISS"],
                },
                {
                    "id": uuid.UUID("1e1b0263-7e49-4c00-985a-568927353700"),
                    "name": "Near-Infrared Spectrograph",
                    "short_name": "JWST_NIRSPEC",
                    "reference_url": "https://jwst-docs.stsci.edu/jwst-near-infrared-spectrograph",
                    "type": InstrumentType.SPECTROSCOPIC_HIGH_RES.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": NIRSPEC_FOOTPRINT,
                    "filters": JWST_FILTERS["JWST_NIRSPEC"],
                },
            ],
        }
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("cf5cfa4c-8406-4460-aa4e-5680843f6afd"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("fd7b3daf-fbb1-4ad6-a598-574da3d15554"),
                "norad_id": 50463,
                "norad_satellite_name": "JWST",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("bdc10f3a-ce62-4852-9c0c-110e0faa2fe8"),
        "name": "James Webb Space Telescope",
        "short_name": "JWST",
        "group_admin": {
            "id": uuid.UUID("adf71748-ebf1-4de0-92fb-e24d487a5b51"),
            "name": "JWST Group Admin",
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
