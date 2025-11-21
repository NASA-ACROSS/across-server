"""rubin observatory migration

Revision ID: 4ee34eaed3a2
Revises: 2a3f02d11576
Create Date: 2025-11-18 15:27:35.792405

"""

import uuid
from datetime import datetime
from typing import Sequence, Union

from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import AltAzConstraint
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_10_03 as snapshot_models
from across_server.core.enums.ephemeris_type import EphemerisType
from across_server.core.enums.instrument_fov import InstrumentFOV
from across_server.core.enums.instrument_type import InstrumentType
from across_server.core.enums.observatory_type import ObservatoryType
from migrations.build_records import ssa_records
from migrations.util.footprint_util import (
    project_footprint,
    square_footprint,
)

# revision identifiers, used by Alembic.
revision: str = "4ee34eaed3a2"
down_revision: Union[str, None] = "2a3f02d11576"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""
The LSST camera is composed of 21 equally sized rafts that each house 3x3 equally sized ccds
Each ccd spatially covers an area of 0.22 deg x 0.22 deg. With the footprint having a width of 15 ccds,
that equals 3.3 degrees of imaging length; leaving 0.2 deg of chip gaps (3.5-3.3). With each row having
14 gaps, that leaves each chip gap to be (0.2/14.0 = 0.01428671 deg).

Each raft has 3 ccds and 2 gaps, leaving a size of a raft (0.22*3 + 0.01428671*2) = 0.68857143 deg.

The focal plane of the camera looks like.

                Rafts
          ----- ----- -----
          | 1 | | 2 | | 3 |
    ----- ----- ----- ----- -----
    | 4 | | 5 | | 6 | | 7 | | 8 |
    ----- ----- ----- ----- -----
    ----- ----- ----- ----- -----
    | 9 | |10 | |11 | |12 | |13 |
    ----- ----- ----- ----- -----
    ----- ----- ----- ----- -----
    |14 | |15 | |16 | |17 | |18 |
    ----- ----- ----- ----- -----
          ----- ----- -----
          |19 | |20 | |21 |
          ----- ----- -----

                Edges
          ----- ----- -----
          |               |
          |               |
    -----                   -----
    |                           |
    |                           |
    |                           |
    |                           |
    |                           |
    -----                  -----
          |                |
          |                |
          ----- ----- -----
"""
raft_length = 0.68857143  # deg
gap_size = 0.01428571  # deg

shift_size = raft_length + gap_size

raft_footprint = square_footprint(length_deg=raft_length)

LSST_RAFTS_FOOTPRINT = [
    # 1st row (top)
    project_footprint(
        raft_footprint, ra_deg=-1.0 * shift_size, dec_deg=2.0 * shift_size
    )[0],  # 1
    project_footprint(raft_footprint, ra_deg=0.0, dec_deg=2.0 * shift_size)[0],  # 2
    project_footprint(raft_footprint, ra_deg=shift_size, dec_deg=2.0 * shift_size)[
        0
    ],  # 3
    # 2nd row
    project_footprint(raft_footprint, ra_deg=-2.0 * shift_size, dec_deg=shift_size)[
        0
    ],  # 4
    project_footprint(raft_footprint, ra_deg=-1.0 * shift_size, dec_deg=shift_size)[
        0
    ],  # 5
    project_footprint(raft_footprint, ra_deg=0.0, dec_deg=shift_size)[0],  # 6
    project_footprint(raft_footprint, ra_deg=shift_size, dec_deg=shift_size)[0],  # 7
    project_footprint(raft_footprint, ra_deg=2.0 * shift_size, dec_deg=shift_size)[
        0
    ],  # 8
    # 3rd row
    project_footprint(raft_footprint, ra_deg=-2.0 * shift_size, dec_deg=0.0)[0],  # 9
    project_footprint(raft_footprint, ra_deg=-1.0 * shift_size, dec_deg=0.0)[0],  # 10
    project_footprint(raft_footprint, ra_deg=0.0, dec_deg=0.0)[0],  # 11
    project_footprint(raft_footprint, ra_deg=shift_size, dec_deg=0.0)[0],  # 12
    project_footprint(raft_footprint, ra_deg=2.0 * shift_size, dec_deg=0.0)[0],  # 13
    # 4th row
    project_footprint(
        raft_footprint, ra_deg=-2.0 * shift_size, dec_deg=-1.0 * shift_size
    )[0],  # 14
    project_footprint(
        raft_footprint, ra_deg=-1.0 * shift_size, dec_deg=-1.0 * shift_size
    )[0],  # 15
    project_footprint(raft_footprint, ra_deg=0.0, dec_deg=-1.0 * shift_size)[0],  # 16
    project_footprint(raft_footprint, ra_deg=shift_size, dec_deg=-1.0 * shift_size)[
        0
    ],  # 17
    project_footprint(
        raft_footprint, ra_deg=2.0 * shift_size, dec_deg=-1.0 * shift_size
    )[0],  # 18
    # 5th row (bottom)
    project_footprint(
        raft_footprint, ra_deg=-1.0 * shift_size, dec_deg=-2.0 * shift_size
    )[0],  # 19
    project_footprint(raft_footprint, ra_deg=0.0, dec_deg=-2.0 * shift_size)[0],  # 20
    project_footprint(raft_footprint, ra_deg=shift_size, dec_deg=-2.0 * shift_size)[
        0
    ],  # 21
]

LSST_EDGES_FOOTPRINT = [
    [
        {
            "x": -1.0 * (1.5 * raft_length + gap_size),
            "y": 2.5 * raft_length + 2.0 * gap_size,
        },
        {"x": 1.5 * raft_length + gap_size, "y": 2.5 * raft_length + 2.0 * gap_size},
        {"x": 1.5 * raft_length + gap_size, "y": 1.5 * raft_length + 1.0 * gap_size},
        {
            "x": 2.5 * raft_length + 2.0 * gap_size,
            "y": 1.5 * raft_length + 1.0 * gap_size,
        },
        {
            "x": 2.5 * raft_length + 2.0 * gap_size,
            "y": -1.0 * (1.5 * raft_length + 1.0 * gap_size),
        },
        {
            "x": 1.5 * raft_length + gap_size,
            "y": -1.0 * (1.5 * raft_length + 1.0 * gap_size),
        },
        {
            "x": 1.5 * raft_length + gap_size,
            "y": -1.0 * (2.5 * raft_length + 2.0 * gap_size),
        },
        {
            "x": -1.0 * (1.5 * raft_length + gap_size),
            "y": -1.0 * (2.5 * raft_length + 2.0 * gap_size),
        },
        {
            "x": -1.0 * (1.5 * raft_length + gap_size),
            "y": -1.0 * (1.5 * raft_length + 1.0 * gap_size),
        },
        {
            "x": -1.0 * (2.5 * raft_length + 2.0 * gap_size),
            "y": -1.0 * (1.5 * raft_length + 1.0 * gap_size),
        },
        {
            "x": -1.0 * (2.5 * raft_length + 2.0 * gap_size),
            "y": 1.5 * raft_length + 1.0 * gap_size,
        },
        {
            "x": -1.0 * (1.5 * raft_length + 1.0 * gap_size),
            "y": 1.5 * raft_length + 1.0 * gap_size,
        },
        {
            "x": -1.0 * (1.5 * raft_length + gap_size),
            "y": 2.5 * raft_length + 2.0 * gap_size,
        },
    ]
]

FILTERS = [
    {
        "id": uuid.UUID("706a1786-2199-4e8e-8e6d-eaf915a0288b"),
        "name": "Rubin u",
        "min_wavelength": 3724 - 463 / 2.0,
        "max_wavelength": 3724 + 463 / 2.0,
        "is_operational": True,
        "reference_url": "https://lsstcam.lsst.io/#filters",
    },
    {
        "id": uuid.UUID("d9cec638-8398-4753-a00a-e4d3f323b97b"),
        "name": "Rubin g",
        "min_wavelength": 4807 - 1485 / 2.0,
        "max_wavelength": 4807 + 1485 / 2.0,
        "is_operational": True,
        "reference_url": "https://lsstcam.lsst.io/#filters",
    },
    {
        "id": uuid.UUID("737c7b2c-2d72-4eed-ac21-463d1d3e0ec9"),
        "name": "Rubin r",
        "min_wavelength": 6221 - 1399 / 2.0,
        "max_wavelength": 6221 + 1399 / 2.0,
        "is_operational": True,
        "reference_url": "https://lsstcam.lsst.io/#filters",
    },
    {
        "id": uuid.UUID("b7d3df49-4e66-4873-bddb-6a8941bcc94d"),
        "name": "Rubin i",
        "min_wavelength": 7559 - 1286 / 2.0,
        "max_wavelength": 7559 + 1286 / 2.0,
        "is_operational": True,
        "reference_url": "https://lsstcam.lsst.io/#filters",
    },
    {
        "id": uuid.UUID("fac2be99-6279-4c56-a6a8-c71595367414"),
        "name": "Rubin z",
        "min_wavelength": 8680 - 1040 / 2.0,
        "max_wavelength": 8680 + 1040 / 2.0,
        "is_operational": True,
        "reference_url": "https://lsstcam.lsst.io/#filters",
    },
    {
        "id": uuid.UUID("ac7c2b7b-d784-4d69-91de-c56c24b812c9"),
        "name": "Rubin y",
        "min_wavelength": 9753 - 862 / 2.0,
        "max_wavelength": 9753 + 862 / 2.0,
        "is_operational": True,
        "reference_url": "https://lsstcam.lsst.io/#filters",
    },
]

OBSERVATORY: dict = {
    "id": uuid.UUID("6e4c4b89-0519-49d2-a69e-3b220aefa065"),
    "name": "Vera C. Rubin Observatory",
    "short_name": "Rubin",
    "type": ObservatoryType.GROUND_BASED.value,
    "reference_url": "https://rubinobservatory.org/",
    "operational_begin_date": datetime(2026, 1, 1, 0, 0, 0),
    "telescopes": [
        {
            "id": uuid.UUID("d18710e4-2a21-4dc6-8a57-eff0f46fc5f7"),
            "name": "Simonyi Survey Telescope",
            "short_name": "LSST",
            "reference_url": "https://rubinobservatory.org/for-scientists/rubin-101/telescopes",
            "instruments": [
                {
                    "id": uuid.UUID("b9342e4c-1106-4e47-a434-30c639ce661b"),
                    "name": "LSST Camera",
                    "short_name": "LSSTCam",
                    "reference_url": "https://rubinobservatory.org/for-scientists/rubin-101/instruments",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": LSST_EDGES_FOOTPRINT,
                    "filters": FILTERS,
                }
            ],
            "constraints": [
                {
                    "id": uuid.UUID("d5ef63c0-7d5d-4712-8d77-67f663866ea5"),
                    "constraint_type": ConstraintType.ALT_AZ,
                    "constraint_parameters": AltAzConstraint(
                        altitude_max=87.0
                    ).model_dump(),
                }
            ],
        }
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("fb370422-a8cb-4b55-ad4c-e7470d87a3d3"),
            "ephemeris_type": EphemerisType.GROUND,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("e0919e38-0a6c-43e3-8f08-ec4b63d8d2e3"),
                "latitude": -30.2446,
                "longitude": -70.7494,
                "height": 2647,
            },
        },
    ],
    "group": {
        "id": uuid.UUID("d513922f-3427-4b30-8d8f-b042204aac61"),
        "name": "Vera C. Rubin Observatory",
        "short_name": "Rubin",
        "group_admin": {
            "id": uuid.UUID("d265190f-512c-48f5-b193-1b3da3ad38ee"),
            "name": "Rubin Group Admin",
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
