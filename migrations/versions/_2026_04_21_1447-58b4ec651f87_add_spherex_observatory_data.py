"""add spherex observatory data

Revision ID: 58b4ec651f87
Revises: a99c9ee52dce
Create Date: 2026-04-21 14:47:22.948075

"""

import uuid
from datetime import datetime
from typing import Sequence, Union

from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums
from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import (
    EarthLimbConstraint,
    MoonAngleConstraint,
    SunAngleConstraint,
)
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_04_21 as snapshot_models
from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from across_server.core.enums.observation_strategy import ObservationStrategy
from across_server.core.enums.observatory_type import ObservatoryType
from across_server.core.enums.visibility_type import VisibilityType
from migrations.build_records import ssa_records
from migrations.util.footprint_util import rectangle_footprint

# revision identifiers, used by Alembic.
revision: str = "58b4ec651f87"
down_revision: Union[str, None] = "a99c9ee52dce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""
SPHEREx is an imaging spectrometer that is conducting a near-infrared spectral survey
of the entire sky. It has a rectangular 3.5 x 11.5 deg FOV.

SPHEREx is unique in that each detector has a spatially-varying central wavelength.
What that means is that where an object is on the detector dictates what wavelength
it is observed in. In other words, each bandpass effectively acts as a mini grism
with 17 resolution elements. Therefore, a given observation will not cover the full
wavelength range of a bandpass for each coordinate in the field of view. However,
for our purposes we can just define the below relatively broad bandpasses.

SPHEREx must maintain pointings > 93.5 degrees from the sun, > 32 degrees from the moon,
and cannot point > 45 degrees from local zenith (equivalent to < 135 degrees from the Earth limb).

More information about SPHEREx's design, bandpasses, and constraints can be found in these papers:
 - https://ui.adsabs.harvard.edu/abs/2026ApJ...999..139B/abstract
 - https://ui.adsabs.harvard.edu/abs/2020SPIE11443E..0IC/abstract
"""
SPHEREX_FOOTPRINT = rectangle_footprint(width_deg=3.5, height_deg=11.5)

SPHEREX_BAND_1 = WavelengthBandpass(
    filter_name="SPHEREx Band 1",
    min=0.75,
    max=1.11,
    unit=tools_enums.WavelengthUnit.MICRON,
)
SPHEREX_BAND_2 = WavelengthBandpass(
    filter_name="SPHEREx Band 2",
    min=1.11,
    max=1.64,
    unit=tools_enums.WavelengthUnit.MICRON,
)
SPHEREX_BAND_3 = WavelengthBandpass(
    filter_name="SPHEREx Band 3",
    min=1.64,
    max=2.42,
    unit=tools_enums.WavelengthUnit.MICRON,
)
SPHEREX_BAND_4 = WavelengthBandpass(
    filter_name="SPHEREx Band 4",
    min=2.42,
    max=3.82,
    unit=tools_enums.WavelengthUnit.MICRON,
)
SPHEREX_BAND_5 = WavelengthBandpass(
    filter_name="SPHEREx Band 5",
    min=3.82,
    max=4.42,
    unit=tools_enums.WavelengthUnit.MICRON,
)
SPHEREX_BAND_6 = WavelengthBandpass(
    filter_name="SPHEREx Band 6",
    min=4.42,
    max=5.00,
    unit=tools_enums.WavelengthUnit.MICRON,
)


OBSERVATORY: dict = {
    "id": uuid.UUID("8af7c8c9-3362-430a-8156-0d1e38808098"),
    "name": "Spectro-Photometer for the History of the Universe, Epoch of Reionization, and Ices Explorer",
    "short_name": "SPHEREx",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://spherex.caltech.edu",
    "operational_begin_date": datetime(2025, 5, 1, 0, 0, 0),
    "telescopes": [
        {
            "id": uuid.UUID("0c8163cd-aff1-445e-9dc2-ec396aab0340"),
            "name": "Spectro-Photometer for the History of the Universe, Epoch of Reionization, and Ices Explorer",
            "short_name": "SPHEREx",
            "is_operational": True,
            "reference_url": "https://spherex.caltech.edu",
            "instruments": [
                {
                    "id": uuid.UUID("fbe30ef9-bb88-454d-81a8-01cdc043a1d2"),
                    "name": "Spectro-Photometer for the History of the Universe, Epoch of Reionization, and Ices Explorer",
                    "short_name": "SPHEREx",
                    "type": InstrumentType.IMAGING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": SPHEREX_FOOTPRINT,
                    "reference_url": "https://spherex.caltech.edu/page/instrument",
                    "visibility_type": VisibilityType.EPHEMERIS.value,
                    "observation_strategy": ObservationStrategy.SURVEY.value,
                    "filters": [
                        {
                            "id": uuid.UUID("71afe5a7-675e-4342-bb7c-3531e67d5778"),
                            "name": SPHEREX_BAND_1.filter_name,
                            "min_wavelength": SPHEREX_BAND_1.min,
                            "max_wavelength": SPHEREX_BAND_1.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("b87bb481-572c-4648-9822-66020e150f75"),
                            "name": SPHEREX_BAND_2.filter_name,
                            "min_wavelength": SPHEREX_BAND_2.min,
                            "max_wavelength": SPHEREX_BAND_2.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("5fad0293-e05f-4f8f-b8a5-1078cbe9eb61"),
                            "name": SPHEREX_BAND_3.filter_name,
                            "min_wavelength": SPHEREX_BAND_3.min,
                            "max_wavelength": SPHEREX_BAND_3.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("303bca68-4b46-4c6e-a166-1fc68772bf5c"),
                            "name": SPHEREX_BAND_4.filter_name,
                            "min_wavelength": SPHEREX_BAND_4.min,
                            "max_wavelength": SPHEREX_BAND_4.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("7e395b0e-a51e-448c-ad0d-becee5a151e5"),
                            "name": SPHEREX_BAND_5.filter_name,
                            "min_wavelength": SPHEREX_BAND_5.min,
                            "max_wavelength": SPHEREX_BAND_5.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("dbd210bb-b2d2-48a5-84c3-edcee3ebf657"),
                            "name": SPHEREX_BAND_6.filter_name,
                            "min_wavelength": SPHEREX_BAND_6.min,
                            "max_wavelength": SPHEREX_BAND_6.max,
                            "is_operational": True,
                        },
                    ],
                },
            ],
            "constraints": [
                {
                    "id": uuid.UUID("de4b2fbb-93e9-4074-845a-336964de0820"),
                    "constraint_type": ConstraintType.EARTH,
                    "constraint_parameters": EarthLimbConstraint(
                        min_angle=135.0,
                    ).model_dump(),
                },
                {
                    "id": uuid.UUID("2720b72d-0797-4f31-bde1-d54dccde093c"),
                    "constraint_type": ConstraintType.MOON,
                    "constraint_parameters": MoonAngleConstraint(
                        min_angle=32.0,
                    ).model_dump(),
                },
                {
                    "id": uuid.UUID("6b6cbc6f-c2ec-423e-89cc-ed5f6cf03f56"),
                    "constraint_type": ConstraintType.SUN,
                    "constraint_parameters": SunAngleConstraint(
                        min_angle=93.5,
                    ).model_dump(),
                },
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("08e0d5a5-02df-4aa6-8914-32186298c51d"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("2fc62417-001e-450a-966c-0b731db14868"),
                "norad_id": 63182,
                "norad_satellite_name": "SPHEREX",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("984db8bc-d347-40f9-98f0-c7e3d8fc5619"),
        "name": "Spectro-Photometer for the History of the Universe, Epoch of Reionization, and Ices Explorer",
        "short_name": "SPHEREx",
        "group_admin": {
            "id": uuid.UUID("cc4ec1c1-e553-4e9a-9847-259181cd6c78"),
            "name": "SPHEREx Group Admin",
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
