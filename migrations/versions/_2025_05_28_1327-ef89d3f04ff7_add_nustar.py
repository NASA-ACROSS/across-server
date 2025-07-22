"""add NuSTAR

Revision ID: ef89d3f04ff7
Revises: 7264308ca648
Create Date: 2025-05-28 13:27:59.884336

"""

import uuid
from typing import Sequence, Union

from across.tools import EnergyBandpass, convert_to_wave
from across.tools.core import enums as tools_enums
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_05_15 as snapshot_models
from across_server.core.enums import InstrumentFOV, InstrumentType, ObservatoryType
from across_server.core.enums.ephemeris_type import EphemerisType
from migrations.build_records import ssa_records
from migrations.util.footprint_util import arcmin_to_deg

# revision identifiers, used by Alembic.
revision: str = "ef89d3f04ff7"
down_revision: Union[str, None] = "7264308ca648"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# NuSTAR has an effective FoV of 10' at 10 keV:
# https://heasarc.gsfc.nasa.gov/docs/nustar/nustar_tech_desc.html
NUSTAR_FOOTPRINT: list[list[dict]] = [
    [
        {"x": arcmin_to_deg(-5.0), "y": arcmin_to_deg(-5.0)},
        {"x": arcmin_to_deg(5.0), "y": arcmin_to_deg(-5.0)},
        {"x": arcmin_to_deg(5.0), "y": arcmin_to_deg(5.0)},
        {"x": arcmin_to_deg(-5.0), "y": arcmin_to_deg(5.0)},
        {"x": arcmin_to_deg(-5.0), "y": arcmin_to_deg(-5.0)},
    ]
]

# Table 2 of the NuSTAR observatory guide
NUSTAR_ENERGY_BANDPASS = EnergyBandpass(
    min=3.0,
    max=78.4,
    unit=tools_enums.EnergyUnit.keV,
)
NUSTAR_WAVELENGTH_BANDPASS = convert_to_wave(NUSTAR_ENERGY_BANDPASS)

OBSERVATORY = {
    "name": "Nuclear Spectroscopic Telescope Array",
    "short_name": "NuSTAR",
    "id": uuid.UUID("afc0ceca-bc57-4d38-a846-c5c36d62256a"),
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://nustar.caltech.edu",
    "is_operational": True,
    "telescopes": [
        {
            "name": "Nuclear Spectroscopic Telescope Array",
            "short_name": "NuSTAR",
            "id": uuid.UUID("281a5a5d-3629-4aa3-a739-968bee65415f"),
            "reference_url": "https://nustar.caltech.edu",
            "is_operational": True,
            "instruments": [
                {
                    "name": "Focal Plane Module A/B",
                    "short_name": "FPM A/B",
                    "id": uuid.UUID("8e3f11f7-c943-4b45-b55e-59d475a4114f"),
                    "reference_url": "https://nustar.caltech.edu",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": NUSTAR_FOOTPRINT,
                    "is_operational": True,
                    "type": InstrumentType.CALORIMETER.value,
                    "filters": [
                        {
                            "name": "NuSTAR Bandpass",
                            "id": uuid.UUID("292c3056-4e95-4bd5-9ed8-66f07e2cc809"),
                            "min_wavelength": NUSTAR_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": NUSTAR_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        }
                    ],
                }
            ],
        }
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("9e82750a-1b38-43ff-ab0e-05f10d8e571e"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("70c7170b-443d-49cc-a38f-de20795e090d"),
                "norad_id": 38358,
                "norad_satellite_name": "NUSTAR",
            },
        }
    ],
    "group": {
        "id": uuid.UUID("98d4cabd-6dd4-48a9-a437-8e562ed3bdbd"),
        "name": "Nuclear Spectroscopic Telescope Array",
        "short_name": "NuSTAR",
        "group_admin": {
            "id": uuid.UUID("feda1a8f-2475-4092-a07e-2fd50fe76f41"),
            "name": "NuSTAR Group Admin",
        },
    },
}


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    records = ssa_records.build(session, OBSERVATORY, snapshot_models)

    session.add_all(records)
    session.commit()
    # ### end Alembic commands ###


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    ssa_records.delete(session, OBSERVATORY, snapshot_models)

    session.commit()
    # ### end Alembic commands ###
