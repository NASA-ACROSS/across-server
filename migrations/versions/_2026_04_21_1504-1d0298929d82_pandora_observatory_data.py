"""pandora observatory data

Revision ID: 1d0298929d82
Revises: 58b4ec651f87
Create Date: 2026-04-21 15:04:36.524515

"""

import uuid
from datetime import datetime
from typing import Sequence, Union

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
from migrations.util.footprint_util import arcsec_to_deg, square_footprint

# revision identifiers, used by Alembic.
revision: str = "1d0298929d82"
down_revision: Union[str, None] = "58b4ec651f87"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""
There isn't any information in the published documents on the FOV of the VISDA instrument
These values are taken from https://github.com/PandoraMission/pandora-sat/blob/main/src/pandorasat/visibledetector.py file,
and are used to calculate the FOV. It assumes that the entire 2048x2048 detector encompasses the image at the pixel scale.

These values come to a square FOV of 0.445 degree sides.
"""
pixel_scale = 0.78301  # arcsec / pixel
detector_shape = 2048  # pixel

PANDORA_VISDA_FOOTPRINT = square_footprint(arcsec_to_deg(pixel_scale * detector_shape))

VISDA_FILTERS = [
    {
        "id": uuid.UUID("66511f07-f27b-4a60-bb00-f6b113eef11d"),
        "name": "VISDA",
        "min_wavelength": 4000,
        "max_wavelength": 6500,
        "is_operational": True,
        "reference_url": "https://arxiv.org/pdf/2108.06438",
    },
]

NIRDA_FILTERS = [
    {
        "id": uuid.UUID("4f8088ce-dcf1-42dd-ad79-b774a2f5c646"),
        "name": "NIRDA",
        "min_wavelength": 10000,
        "max_wavelength": 16000,
        "is_operational": True,
        "reference_url": "https://arxiv.org/pdf/2108.06438",
    },
]

OBSERVATORY: dict = {
    "id": uuid.UUID("d5417cb0-5f4f-4e79-9a81-49eb77cfaea7"),
    "name": "Pandora Observatory",
    "short_name": "Pandora",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://pandorasat.com/",
    "operational_begin_date": datetime(2026, 1, 12, 0, 0, 0),
    "telescopes": [
        {
            "id": uuid.UUID("0b85e647-ffd6-4342-9183-d4e214ce02a2"),
            "name": "Pandora Observatory",
            "short_name": "Pandora",
            "reference_url": "https://pandorasat.com/",
            "is_operational": True,
            "instruments": [
                {
                    "id": uuid.UUID("5865b62e-179f-4e5b-9cd0-692d1ed84d4a"),
                    "name": "Visible Detector",
                    "short_name": "VISDA",
                    "reference_url": "http://pandorasat.com/about/#pandora-payload",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": PANDORA_VISDA_FOOTPRINT,
                    "filters": VISDA_FILTERS,
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "observation_strategy": ObservationStrategy.POINTED,
                    "is_operational": True,
                },
                {
                    "id": uuid.UUID("6153c306-d100-4118-b859-b7230ff0480e"),
                    "name": "NIR Detector",
                    "short_name": "NIRDA",
                    "reference_url": "http://pandorasat.com/about/#pandora-payload",
                    "type": InstrumentType.SPECTROSCOPIC_LOW_RES.value,
                    "field_of_view": InstrumentFOV.POINT.value,
                    "filters": NIRDA_FILTERS,
                    "footprint": [],
                    "visibility_type": VisibilityType.EPHEMERIS,
                    "observation_strategy": ObservationStrategy.POINTED,
                    "is_operational": True,
                },
            ],
            # constraint information taken from section 2.1 of https://arxiv.org/pdf/2305.02285
            "constraints": [
                {
                    "id": uuid.UUID("86398a06-4d2c-4765-aece-be1697cefd82"),
                    "constraint_type": ConstraintType.SUN,
                    "constraint_parameters": {"min_angle": 90},
                },
                {
                    "id": uuid.UUID("9429b370-c6c1-4a14-afac-6040de3f9bbe"),
                    "constraint_type": ConstraintType.EARTH,
                    "constraint_parameters": {"min_angle": 20},
                },
                {
                    "id": uuid.UUID("0d417d1c-50b8-4c35-8d12-ab4b3a93c851"),
                    "constraint_type": ConstraintType.MOON,
                    "constraint_parameters": {"min_angle": 40},
                },
            ],
        }
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("2a65aa6a-5999-4e1c-b149-0aeecf1dc8fb"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("fa45448e-6aac-45dd-8101-3c1a58390c88"),
                "norad_id": 67395,
                "norad_satellite_name": "PANDORA",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("5a34835c-133f-447c-afc7-c5a9ea3c05e9"),
        "name": "Pandora Observatory",
        "short_name": "Pandora",
        "group_admin": {
            "id": uuid.UUID("5eb34da5-53dd-4f0c-9320-8cedd059f1ca"),
            "name": "Pandora Group Admin",
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
