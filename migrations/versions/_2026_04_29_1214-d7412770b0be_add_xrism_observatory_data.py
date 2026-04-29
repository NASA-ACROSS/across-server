"""add xrism observatory data

Revision ID: d7412770b0be
Revises: 1d0298929d82
Create Date: 2026-04-29 12:14:58.813841

"""

import uuid
from datetime import datetime
from typing import Sequence, Union

from across.tools import EnergyBandpass, convert_to_wave
from across.tools import enums as tools_enums
from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import (
    EarthLimbConstraint,
    MoonAngleConstraint,
    SAAPolygonConstraint,
    SunAngleConstraint,
)
from alembic import op
from shapely import Polygon
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_04_21 as snapshot_models
from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from across_server.core.enums.observation_strategy import ObservationStrategy
from across_server.core.enums.observatory_type import ObservatoryType
from across_server.core.enums.visibility_type import VisibilityType
from migrations.build_records import ssa_records
from migrations.util.footprint_util import (
    arcmin_to_deg,
    project_footprint,
    square_footprint,
)

# revision identifiers, used by Alembic.
revision: str = "d7412770b0be"
down_revision: Union[str, None] = "1d0298929d82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""
XRISM is an X-ray mission with imaging and spectroscopic capabilities.
It has two instruments: Resolve, a high-resolution X-ray calorimeter,
and Xtend, a wide-field X-ray imager. Each instrument has a slightly different bandpass,
but both are sensitive to roughly the energy range of 0.5 - 12 keV. Each instrument is
technically on a separate X-ray Mirror Assembly (XMA) telescope, but since they are identical
and roughly co-aligned, here we can treat them as one telescope with two instruments.

Resolve has a narrow, square field of view while Xtend has a wider field,
made up of four square CCDs arranged in a 2x2 pattern with small chip gaps between them.

XRISM can only point between 60 and 120 degrees relative to the Sun. Additionally, it cannot
point at the Earth or the moon--exact angles for these constraints are not given, so we will
assume standard 20 degree separaiton constraints for each. Finally, XRISM is in LEO and does not produce
scientifically useful observations while passing through the SAA.

References:
  - https://www.xrism.jaxa.jp/en/technology/
  - https://science.nasa.gov/mission/xrism/spacecraft/
  - https://heasarc.gsfc.nasa.gov/docs/xrism/proposals/POG/xrism_pog.pdf
  - https://heasarc.gsfc.nasa.gov/docs/xrism/calib/index.html
"""

### Resolve
RESOLVE_FOOTPRINT = square_footprint(length_deg=arcmin_to_deg(3.0))

RESOLVE_BANDPASS = convert_to_wave(
    EnergyBandpass(
        filter_name="XRISM Resolve",
        min=1.7,
        max=12.0,
        unit=tools_enums.EnergyUnit.keV,
    )
)

### Xtend
"""
Xtend has a field of view made up of four square CCDs, each 18.9' x 18.9',
arranged in a 2x2 pattern with 0.7' gaps between them:
     18.9' 0.7' 18.9'
    -----      -----
    |   |      |   | 18.9'
    -----      -----
                     0.7'
    -----      -----
    |   |      |   | 18.9'
    -----      -----
"""
XTEND_CCD = square_footprint(length_deg=arcmin_to_deg(18.9))

XTEND_FOOTPRINT = [
    # Top left: dx=-(18.9/2 + 0.7/2) dy=(18.9+45)
    project_footprint(
        XTEND_CCD,
        ra_deg=-arcmin_to_deg(18.9 / 2 + 0.7 / 2),
        dec_deg=arcmin_to_deg(18.9 / 2 + 0.7 / 2),
    )[0],
    # Top right: dx=(18.9/2 + 0.7/2) dy=(18.9/2 + 0.7/2)
    project_footprint(
        XTEND_CCD,
        ra_deg=arcmin_to_deg(18.9 / 2 + 0.7 / 2),
        dec_deg=arcmin_to_deg(18.9 / 2 + 0.7 / 2),
    )[0],
    # Bottom right: dx=(18.9/2 + 0.7/2) dy=-(18.9/2 + 0.7/2)
    project_footprint(
        XTEND_CCD,
        ra_deg=arcmin_to_deg(18.9 / 2 + 0.7 / 2),
        dec_deg=-arcmin_to_deg(18.9 / 2 + 0.7 / 2),
    )[0],
    # Bottom left: dx=(18.9/2 + 0.7/2) dy=-(18.9/2 + 0.7/2)
    project_footprint(
        XTEND_CCD,
        ra_deg=-arcmin_to_deg(18.9 / 2 + 0.7 / 2),
        dec_deg=-arcmin_to_deg(18.9 / 2 + 0.7 / 2),
    )[0],
]

XTEND_BANDPASS = convert_to_wave(
    EnergyBandpass(
        filter_name="XRISM Xtend",
        min=0.4,
        max=13.0,
        unit=tools_enums.EnergyUnit.keV,
    )
)

### Xrism SAA Polygon
### from https://heasarc.gsfc.nasa.gov/docs/xrism/calib/index.html
XRISM_SAA_POLYGON = Polygon(
    [
        (-84.0, -35.0),
        (-92.0, -24.0),
        (-92.0, -12.0),
        (-66.0, 0.0),
        (-36.0, 0.0),
        (0.0, -20.0),
        (4.0, -22.0),
        (20.0, -22.0),
        (20.0, -35.0),
        (-84.0, -35.0),
    ]
)

OBSERVATORY: dict = {
    "id": uuid.UUID("050cae97-6f92-4ee5-909f-19c79f8b13bd"),
    "name": "X-ray Imaging and Spectroscopy Mission",
    "short_name": "XRISM",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://www.xrism.jaxa.jp/en/",
    "operational_begin_date": datetime(2023, 9, 7, 0, 0, 0),
    "telescopes": [
        {
            "id": uuid.UUID("da146080-ddd8-4b4b-9be5-bc1f71763dc1"),
            "name": "X-ray Mirror Assembly",
            "short_name": "XMA",
            "is_operational": True,
            "reference_url": "https://www.xrism.jaxa.jp/en/technology/",
            "instruments": [
                {
                    "id": uuid.UUID("8d9a6fe9-330b-4ba6-83d3-506a1609b199"),
                    "name": "Resolve",
                    "short_name": "Resolve",
                    "type": InstrumentType.CALORIMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": RESOLVE_FOOTPRINT,
                    "reference_url": "https://www.xrism.jaxa.jp/en/technology/",
                    "visibility_type": VisibilityType.EPHEMERIS.value,
                    "observation_strategy": ObservationStrategy.POINTED.value,
                    "filters": [
                        {
                            "id": uuid.UUID("9693d1c8-d9ae-4309-a3b2-6dee7e862e96"),
                            "name": RESOLVE_BANDPASS.filter_name,
                            "min_wavelength": RESOLVE_BANDPASS.min,
                            "max_wavelength": RESOLVE_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
                {
                    "id": uuid.UUID("0c94d3eb-fcad-4918-8e6b-4b2ce5a00d79"),
                    "name": "Xtend",
                    "short_name": "Xtend",
                    "type": InstrumentType.XRAY_IMAGING_SPECTROMETER.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": XTEND_FOOTPRINT,
                    "reference_url": "https://www.xrism.jaxa.jp/en/technology/",
                    "visibility_type": VisibilityType.EPHEMERIS.value,
                    "observation_strategy": ObservationStrategy.POINTED.value,
                    "filters": [
                        {
                            "id": uuid.UUID("0454afe5-ad11-473f-8146-30c27ea864b4"),
                            "name": XTEND_BANDPASS.filter_name,
                            "min_wavelength": XTEND_BANDPASS.min,
                            "max_wavelength": XTEND_BANDPASS.max,
                            "is_operational": True,
                        },
                    ],
                },
            ],
            "constraints": [
                {
                    "id": uuid.UUID("b1873232-8da1-4825-9998-23a6a3fcd18b"),
                    "constraint_type": ConstraintType.SUN,
                    "constraint_parameters": SunAngleConstraint(
                        min_angle=60.0,
                        max_angle=120.0,
                    ).model_dump(),
                },
                {
                    "id": uuid.UUID("c512f1fd-69df-445b-a3f7-2d0e39521564"),
                    "constraint_type": ConstraintType.EARTH,
                    "constraint_parameters": EarthLimbConstraint(
                        min_angle=20.0,
                    ).model_dump(),
                },
                {
                    "id": uuid.UUID("5dd7308a-ac3f-48e8-be7c-6bebcf696ea4"),
                    "constraint_type": ConstraintType.MOON,
                    "constraint_parameters": MoonAngleConstraint(
                        min_angle=20.0,
                    ).model_dump(),
                },
                {
                    "id": uuid.UUID("4b95ae52-0386-40f1-b7d5-9a92abd0267d"),
                    "constraint_type": ConstraintType.SAA,
                    "constraint_parameters": SAAPolygonConstraint(
                        polygon=XRISM_SAA_POLYGON,
                    ).model_dump(),
                },
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("72a10424-d57f-4f15-82a9-95f7bae49036"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("98778ce4-13fe-4407-bac2-26c47cebe81f"),
                "norad_id": 57800,
                "norad_satellite_name": "XRISM",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("edbf530b-8883-4ba5-b99d-b1c7a0e6b7ea"),
        "name": "X-ray Imaging and Spectroscopy Mission",
        "short_name": "XRISM",
        "group_admin": {
            "id": uuid.UUID("cd59b683-9cc3-4bee-826f-f059efa0564c"),
            "name": "XRISM Group Admin",
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
