"""add blackcat observatory data

Revision ID: 5e170132081b
Revises: d7412770b0be
Create Date: 2026-05-14 10:14:26.556763

"""

import uuid
from datetime import datetime
from typing import Sequence, Union

from across.tools import EnergyBandpass, convert_to_wave
from across.tools import enums as tools_enums
from across.tools.core.enums import ConstraintType
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_04_21 as snapshot_models
from across_server.core.enums.ephemeris_type import EphemerisType
from across_server.core.enums.instrument_fov import InstrumentFOV
from across_server.core.enums.instrument_type import InstrumentType
from across_server.core.enums.observation_strategy import ObservationStrategy
from across_server.core.enums.observatory_type import ObservatoryType
from across_server.core.enums.visibility_type import VisibilityType
from migrations.build_records import ssa_records
from migrations.util.footprint_util import rectangle_footprint

# revision identifiers, used by Alembic.
revision: str = "5e170132081b"
down_revision: Union[str, None] = "d7412770b0be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""
BlackCAT is a simple observatory with wide field of view and a detector optimized for soft X-rays.
"""

BLACKCAT_FOOTPRINT = rectangle_footprint(width_deg=40.0, height_deg=70.0)

BLACKCAT_ENERGY_BANDPASS = EnergyBandpass(
    min=2.0,
    max=8.0,
    unit=tools_enums.EnergyUnit.keV,
)
BLACKCAT_WAVELENGTH_BANDPASS = convert_to_wave(BLACKCAT_ENERGY_BANDPASS)

BLACKCAT_FILTER = [
    {
        "id": uuid.UUID("b93fbbe3-59aa-4104-bf50-52828846ae67"),
        "name": "BLACKCAT BANDPASS",
        "min_wavelength": BLACKCAT_WAVELENGTH_BANDPASS.min,
        "max_wavelength": BLACKCAT_WAVELENGTH_BANDPASS.max,
        "is_operational": True,
        "reference_url": "https://heasarc.gsfc.nasa.gov/docs/blackcat/",
    },
]


OBSERVATORY: dict = {
    "id": uuid.UUID("4d88443a-ffd7-4d19-bfb7-24da34c16408"),
    "name": "BlackCAT CubeSat",
    "short_name": "BlackCAT",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/blackcat/",
    "operational_begin_date": datetime(2026, 1, 12, 0, 0, 0),
    "telescopes": [
        {
            "id": uuid.UUID("b73421e2-8b39-40cb-911d-7d93d3aa92fb"),
            "name": "BlackCAT CubeSat",
            "short_name": "BlackCAT",
            "reference_url": "https://heasarc.gsfc.nasa.gov/docs/blackcat/",
            "is_operational": True,
            "instruments": [
                {
                    "id": uuid.UUID("14b5acc2-02ab-4499-b8d3-0b3b5aca1553"),
                    "name": "BlackCAT",
                    "short_name": "BlackCAT",
                    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/blackcat/",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": BLACKCAT_FOOTPRINT,
                    "filters": BLACKCAT_FILTER,
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "observation_strategy": ObservationStrategy.POINTED,
                    "is_operational": True,
                }
            ],
            "constraints": [
                {
                    "id": uuid.UUID("56969f38-5bec-4cf9-bea4-26e76b1fd6d5"),
                    "constraint_type": ConstraintType.SUN,
                    "constraint_parameters": {"min_angle": 0},
                },
                {
                    "id": uuid.UUID("50072037-ae61-491d-9915-30127783f8b4"),
                    "constraint_type": ConstraintType.EARTH,
                    "constraint_parameters": {"min_angle": 0},
                },
                {
                    "id": uuid.UUID("0621d393-7db8-45c8-b3f5-d21628e517b2"),
                    "constraint_type": ConstraintType.MOON,
                    "constraint_parameters": {"min_angle": 0},
                },
            ],
        }
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("aa78b80a-de1c-44f8-bc24-c1016066aff3"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("0e46ba3e-88d8-4f0c-91a7-389d31e8f9fe"),
                "norad_id": 67369,
                "norad_satellite_name": "BLACKCAT",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("ec136f65-ef3c-41e7-9723-1f1ef9c3f8f3"),
        "name": "BlackCAT Observatory",
        "short_name": "BlackCAT",
        "group_admin": {
            "id": uuid.UUID("daf03ea5-66a1-47f5-9b3b-1991aa131d7d"),
            "name": "BlackCAT Group Admin",
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
