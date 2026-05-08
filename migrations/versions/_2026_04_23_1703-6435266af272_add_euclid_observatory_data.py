"""add euclid observatory data

Revision ID: 6435266af272
Revises: 1d0298929d82
Create Date: 2026-04-23 17:03:16.031114

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
from migrations.util.footprint_util import rectangle_footprint

# revision identifiers, used by Alembic.
revision: str = "6435266af272"
down_revision: Union[str, None] = "1d0298929d82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

"""
Euclid is a space-based observatory with two instruments (an optical imager and
a near-infrared imager and spectrometer) conducting a survey of 15,000 square degrees.

Euclid has two instruments: the optical imager VIS and the near-infrared imager/spectrometer
NISP. Both have wide, rectangular fields of view. VIS has a single bandpass while NISP has
three infrared bandpasses and two grisms, which conduct slitless spectroscopic observations.

Euclid is in orbit around the L2 point and must maintain pointings between 87 and 104 degrees from the sun,
which defines the survey area at a given time.

References:
  - Euclid mission overview: https://ui.adsabs.harvard.edu/abs/2025A%26A...697A...1E/abstract
  - VIS instrument overview: https://ui.adsabs.harvard.edu/abs/2025A%26A...697A...2E/abstract
  - NISP instrument overview: https://ui.adsabs.harvard.edu/abs/2025A%26A...697A...3E/abstract
"""
VIS_FOOTPRINT = rectangle_footprint(width_deg=0.787, height_deg=0.709)
NISP_FOOTPRINT = rectangle_footprint(width_deg=0.763, height_deg=0.722)

VIS_BANDPASS = WavelengthBandpass(
    filter_name="Euclid VIS",
    min=550,
    max=990,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)

NISP_Y = WavelengthBandpass(
    filter_name="Euclid NISP Y",
    min=920,
    max=1146,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)

NISP_J = WavelengthBandpass(
    filter_name="Euclid NISP J",
    min=1146,
    max=1372,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)

NISP_H = WavelengthBandpass(
    filter_name="Euclid NISP H",
    min=1372,
    max=2000,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)

NISP_RED = WavelengthBandpass(
    filter_name="Euclid NISP Red Grism",
    min=1250,
    max=1850,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)

NISP_BLUE = WavelengthBandpass(
    filter_name="Euclid NISP Blue Grism",
    min=920,
    max=1250,
    unit=tools_enums.WavelengthUnit.NANOMETER,
)


OBSERVATORY: dict = {
    "id": uuid.UUID("d5b1a290-0839-42e6-a8b0-63a55c8bdeb4"),
    "name": "Euclid Observatory",
    "short_name": "Euclid",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://www.cosmos.esa.int/web/euclid/home",
    "operational_begin_date": datetime(2023, 7, 1, 0, 0, 0),
    "telescopes": [
        {
            "id": uuid.UUID("6f80ed81-bc0a-470f-a4dd-16db130911cb"),
            "name": "Euclid Telescope",
            "short_name": "Euclid",
            "is_operational": True,
            "reference_url": "https://www.esa.int/Science_Exploration/Space_Science/Euclid_overview",
            "instruments": [
                {
                    "id": uuid.UUID("7ba162fd-4eb6-485c-bdb9-7c5f38b95935"),
                    "name": "VISible Instrument",
                    "short_name": "Euclid VIS",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": VIS_FOOTPRINT,
                    "reference_url": "https://sci.esa.int/web/euclid/-/euclid-vis-instrument",
                    "visibility_type": VisibilityType.EPHEMERIS.value,
                    "observation_strategy": ObservationStrategy.SURVEY.value,
                    "filters": [
                        {
                            "id": uuid.UUID("96d2b8b0-c639-4204-b31e-95256e248250"),
                            "name": VIS_BANDPASS.filter_name,
                            "min_wavelength": VIS_BANDPASS.min,
                            "max_wavelength": VIS_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("42b791e3-e486-4703-baad-a922cc281e1a"),
                    "name": "Near-Infrared Spectrometer and Photometer",
                    "short_name": "Euclid NISP",
                    "type": InstrumentType.IMAGING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": NISP_FOOTPRINT,
                    "reference_url": "https://sci.esa.int/web/euclid/-/euclid-nisp-instrument",
                    "visibility_type": VisibilityType.EPHEMERIS.value,
                    "observation_strategy": ObservationStrategy.SURVEY.value,
                    "filters": [
                        {
                            "id": uuid.UUID("0a17229a-e537-42b6-99ee-64845ce5c540"),
                            "name": NISP_Y.filter_name,
                            "min_wavelength": NISP_Y.min,
                            "max_wavelength": NISP_Y.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("fed0123b-8bf8-46d8-8ddc-224af4d67dac"),
                            "name": NISP_J.filter_name,
                            "min_wavelength": NISP_J.min,
                            "max_wavelength": NISP_J.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("c13f3fac-63d5-4d1b-9ce1-9b00bee89c01"),
                            "name": NISP_H.filter_name,
                            "min_wavelength": NISP_H.min,
                            "max_wavelength": NISP_H.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("88628630-2c47-40c8-9e6a-c579dd6f7db9"),
                            "name": NISP_BLUE.filter_name,
                            "min_wavelength": NISP_BLUE.min,
                            "max_wavelength": NISP_BLUE.max,
                            "is_operational": True,
                        },
                        {
                            "id": uuid.UUID("e112b90e-a26d-4e33-bb6a-157a2bc1c5d1"),
                            "name": NISP_RED.filter_name,
                            "min_wavelength": NISP_RED.min,
                            "max_wavelength": NISP_RED.max,
                            "is_operational": True,
                        },
                    ],
                },
            ],
            "constraints": [
                {
                    "id": uuid.UUID("e0b47461-3c4e-408a-96d4-0fb2f4ebefd3"),
                    "constraint_type": ConstraintType.SUN,
                    "constraint_parameters": SunAngleConstraint(
                        min_angle=87.0,
                        max_angle=104.0,
                    ).model_dump(),
                },
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("ede2d199-8099-426d-89b4-669695f21648"),
            "ephemeris_type": EphemerisType.JPL.value,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("5429f889-1031-47a2-ac62-ba15a7d1e51e"),
                "naif_id": -680,
            },
        },
        {
            "id": uuid.UUID("f1c5d378-b9df-48ac-a9cc-ab7803a6037e"),
            "ephemeris_type": EphemerisType.TLE.value,
            "priority": 2,
            "parameters": {
                "id": uuid.UUID("95791809-377d-41e5-92ac-4b7d8e77a3f3"),
                "norad_id": 57209,
                "norad_satellite_name": "EUCLID",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("2d0d7068-c315-4d99-b936-55d1bcc26fea"),
        "name": "Euclid Observatory",
        "short_name": "Euclid",
        "group_admin": {
            "id": uuid.UUID("c1e43ffe-3d50-45fb-9e74-06e90219e438"),
            "name": "Euclid Group Admin",
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
