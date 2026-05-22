"""add sparcs observatory data

Revision ID: 572f3bb912a2
Revises: 15fb704e6b6a
Create Date: 2026-05-21 14:21:15.688059

"""

import uuid
from datetime import datetime
from typing import Sequence, Union

from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums
from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import SunAngleConstraint
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_04_21 as snapshot_models
from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from across_server.core.enums.observation_strategy import ObservationStrategy
from across_server.core.enums.observatory_type import ObservatoryType
from across_server.core.enums.visibility_type import VisibilityType
from migrations.build_records import ssa_records
from migrations.util.footprint_util import (
    arcmin_to_deg,
    circular_footprint,
)

# revision identifiers, used by Alembic.
revision: str = "572f3bb912a2"
down_revision: Union[str, None] = "15fb704e6b6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""
The Star-Planet Activity Research CubeSat (SPARCS) is a cube sat conducting a survey of M-dwarf stars in the UV.
It has two filters (FUV and NUV) with which it takes long time-series images of a set of ~20 nearby M-dwarfs.
SPARCS is in a sun-synchronous LEO with pointing constraints primarily set by the orientation of the spacecraft's
solar panels relative to the sun, which enables a roughly 60-degree field of view for continuous observations.

The SPARCS field of view is a circle with a radius of approximately 20'. Targets that are in the FOV
during an observation series may be coincidentally observed, and users can contact the SPARCS team to retrieve photometry
of those targets.

References:
  - SPARCS about page: https://sparcs.asu.edu/about
  - SPARCS instrument documentation: https://doi.org/10.1117/1.JATIS.11.4.042212
  - SPARCS telescope and payload documentation: https://sparcs.asu.edu/sites/g/files/litvpz1881/files/2021-10/scowen_sparcs_spie.pdf
  - SPARCS pointing constraint: https://arxiv.org/pdf/1808.09954
"""

SPARCS_FOOTPRINT = circular_footprint(radius_deg=arcmin_to_deg(20.0))

SPARCS_FUV_BANDPASS = WavelengthBandpass(
    filter_name="SPARCS FUV",
    min=1530,
    max=1710,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)


SPARCS_NUV_BANDPASS = WavelengthBandpass(
    filter_name="SPARCS NUV",
    min=2600,
    max=3000,
    unit=tools_enums.WavelengthUnit.ANGSTROM,
)

OBSERVATORY: dict = {
    "id": uuid.UUID("6c775756-2f1d-47f4-af23-6af83c81e0b1"),
    "name": "Star-Planet Activity Research CubeSat",
    "short_name": "SPARCS",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://sparcs.asu.edu/",
    "operational_begin_date": datetime(2026, 1, 11, 0, 0, 0),
    "telescopes": [
        {
            "id": uuid.UUID("a4fd910c-319f-4b36-b5e0-ca281b1523db"),
            "name": "Star-Planet Activity Research CubeSat",
            "short_name": "SPARCS",
            "is_operational": True,
            "reference_url": "https://sparcs.asu.edu/about",
            "instruments": [
                {
                    "id": uuid.UUID("a894dee5-9994-4c14-b1ee-c84acf26d035"),
                    "name": "Star-Planet Activity Research CubeSat",
                    "short_name": "SPARCS",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": SPARCS_FOOTPRINT,
                    "reference_url": "https://sparcs.asu.edu/about",
                    "visibility_type": VisibilityType.EPHEMERIS.value,
                    "observation_strategy": ObservationStrategy.SURVEY.value,
                    "filters": [
                        {
                            "id": uuid.UUID("00a91d02-6972-4c45-a733-5585588e36c1"),
                            "name": SPARCS_FUV_BANDPASS.filter_name,
                            "min_wavelength": SPARCS_FUV_BANDPASS.min,
                            "max_wavelength": SPARCS_FUV_BANDPASS.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("5a6991b4-fbfd-4d07-8f8b-07cfb43894c4"),
                            "name": SPARCS_NUV_BANDPASS.filter_name,
                            "min_wavelength": SPARCS_NUV_BANDPASS.min,
                            "max_wavelength": SPARCS_NUV_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
            ],
            "constraints": [
                # SPARCS's pointing is primarily constrained by the angle between the solar panel normal vector
                # and the sun, which must be no more than 40 degrees. Given the configuration of the telescope and
                # its sun synchronous orbit, this is equivalent to a sun angle constraint with a minimum angle of 140 degrees.
                {
                    "id": uuid.UUID("9803a943-3125-49da-8a83-2c081dda638e"),
                    "constraint_type": ConstraintType.SUN,
                    "constraint_parameters": SunAngleConstraint(
                        min_angle=140.0,
                    ).model_dump(),
                },
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("910972e1-f893-49d3-b063-aa329ebd6bb7"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("87765c63-58e6-4c46-a462-67d38982027f"),
                "norad_id": 67386,
                "norad_satellite_name": "OBJECT Z",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("adc64e71-c500-40bd-956a-96ae1313ef9f"),
        "name": "Star-Planet Activity Research CubeSat",
        "short_name": "SPARCS",
        "group_admin": {
            "id": uuid.UUID("9287b34e-314b-40c0-95e2-1453c5c1a10b"),
            "name": "SPARCS Group Admin",
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
