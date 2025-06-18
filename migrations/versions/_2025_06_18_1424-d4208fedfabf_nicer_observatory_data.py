"""nicer_observatory_data

Revision ID: d4208fedfabf
Revises: 3809d4ab4e06
Create Date: 2025-06-18 14:24:23.624891

"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

from across.tools import EnergyBandpass, convert_to_wave
from across.tools import enums as tools_enums
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_05_15 as snapshot_models
from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from across_server.core.enums.observatory_type import ObservatoryType
from migrations.build_records import ssa_records
from migrations.db_util import arcmin_to_deg, circular_footprint

# revision identifiers, used by Alembic.
revision: str = "d4208fedfabf"
down_revision: Union[str, None] = "3809d4ab4e06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the NICER footprint as a circular area with a radius of 3 arcminutes
footprint = circular_footprint(radius_deg=arcmin_to_deg(3.0))

NICER_ENERGY_BANDPASS = EnergyBandpass(
    min=0.2,
    max=12.0,
    unit=tools_enums.EnergyUnit.keV,
)
NICER_WAVELENGTH_BANDPASS = convert_to_wave(NICER_ENERGY_BANDPASS)

OBSERVATORY: dict = {
    "id": uuid.UUID("dbf57304-fb1c-4d3b-99b1-6a9f6ade05b3"),
    "name": "Neutron Star Interior Composition Explorer",
    "short_name": "NICER",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/nicer/mission_guide/",
    "telescopes": [
        {
            "id": uuid.UUID("8ca37c8a-8fcc-404b-a58d-a9854099c97d"),
            "name": "Neutron Star Interior Composition Explorer",
            "short_name": "NICER",
            "reference_url": "https://heasarc.gsfc.nasa.gov/docs/nicer/mission_guide/",
            "instruments": [
                {
                    "id": uuid.UUID("74160b93-b3f5-4d9f-b9c9-c9938784d69c"),
                    "name": "X-ray Timing Instrument",
                    "short_name": "XTI",
                    "type": InstrumentType.XRAY_COUNTING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": footprint,
                    "filters": [
                        {
                            "id": uuid.UUID("f8d2fdce-7831-4545-9d23-40a412483bd6"),
                            "name": "NICER XTI",
                            "min_wavelength": NICER_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": NICER_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        }
                    ],
                }
            ],
        }
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("47eca96a-c64b-4b68-93de-1a2c61cd6244"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 2,
            "parameters": {
                "id": uuid.UUID("7591f4eb-6ad3-4c8e-86e7-9e051ca2e707"),
                "norad_id": 25544,
                "norad_satellite_name": "ISS (ZARYA)",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("c38204e4-1bad-4584-91a5-c74cba026031"),
        "name": "Neutron Star Interior Composition Explorer",
        "short_name": "NICER",
        "group_admin": {
            "id": uuid.UUID("d177d066-735f-4f67-8ef3-f00e9c688491"),
            "name": "NICER Group Admin",
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
