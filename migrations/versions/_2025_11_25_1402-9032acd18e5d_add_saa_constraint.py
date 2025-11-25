"""add SAA constraint

Revision ID: 9032acd18e5d
Revises: 4ee34eaed3a2
Create Date: 2025-11-25 14:02:27.152104

"""

import uuid
from typing import Sequence, Union

from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import SAAPolygonConstraint
from alembic import op
from shapely import Polygon
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_10_03 as models

# revision identifiers, used by Alembic.
revision: str = "9032acd18e5d"
down_revision: Union[str, None] = "4ee34eaed3a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

"""
Define SAAPolygonConstraints for instruments that do not observe
when they pass through the SAA.

Each observatory has a different definition of the SAA polygon,
therefore for each we will define a different constraint and associate
it with the relevant instruments.

Here are the sources for the different definitions:
    NICER: CALDB files
        https://heasarc.gsfc.nasa.gov/FTP/caldb/data/nicer/xti/bcf/
    Fermi: orbit simulator
        https://fermi.gsfc.nasa.gov/ssc/data/analysis/scitools/data/OrbSim/L_SAA_2008198.03
    IXPE: ixpeobssim package
        https://github.com/lucabaldini/ixpeobssim/blob/main/ixpeobssim/instrument/data/saa_polygon.txt
        Note that this polygon is the same as Fermi's,
        and the authors state that it's an approximation for IXPE
    HST: costools package
        https://github.com/spacetelescope/costools/blob/master/costools/saamodel.py
        These match the contours defined in STScI Instrument Science Reports (2002-01, 2009-40)
"""

NICER_SAA_POLYGON = Polygon(
    [
        (-67.68, -2.36),
        (-86.40, -10.28),
        (-84.49, -31.85),
        (-72.35, -43.99),
        (-54.56, -52.58),
        (-28.19, -53.63),
        (0.21, -46.89),
        (15.51, -42.67),
        (28.80, -34.04),
        (12.96, -21.08),
        (-9.36, -21.08),
        (-23.76, -16.04),
        (-43.20, 0.52),
        (-67.68, -2.36),
    ]
)

FERMI_IXPE_SAA_POLYGON = Polygon(
    [
        (33.9, -30.0),
        (24.5, -22.6),
        (-18.6, 2.5),
        (-25.7, 5.2),
        (-36.0, 5.2),
        (-42.0, 4.6),
        (-58.8, 0.7),
        (-93.1, -8.6),
        (-97.5, -9.9),
        (-98.5, -12.5),
        (-92.1, -21.7),
        (-86.1, -30.0),
        (33.9, -30.0),
    ]
)

STIS_COS_SAA_POLYGON = Polygon(
    [
        (14.0, -28.3),
        (15.0, -27.5),
        (13.0, -26.1),
        (1.5, -19.8),
        (-19.0, -9.6),
        (-29.6, -7.6),
        (-41.2, -6.0),
        (-62.8, -7.9),
        (-73.9, -12.0),
        (-80.1, -17.1),
        (-82.5, -20.3),
        (-83.5, -23.5),
        (-83.6, -26.0),
        (-83.3, -28.6),
        (14.0, -28.3),
    ]
)

ACS_WFC3_SAA_POLYGON = Polygon(
    [
        (25.0, -28.5),
        (7.0, -16.0),
        (-9.0, -6.5),
        (-19.0, -2.0),
        (-42.0, 1.0),
        (-60.0, -3.0),
        (-70.0, -7.0),
        (-76.0, -10.0),
        (-82.0, -15.0),
        (-87.0, -20.0),
        (-85.0, -30.0),
        (25.0, -28.5),
    ]
)

INSTRUMENT_POLYGONS: list[dict] = [
    {
        "instrument_names": [
            "HST_WFC3_UVIS",
            "HST_WFC3_IR",
            "HST_ACS",
        ],
        "id": uuid.UUID("3b424421-1b06-449d-a493-870c15ac0229"),
        "polygon": ACS_WFC3_SAA_POLYGON,
    },
    {
        "instrument_names": ["HST_COS", "HST_STIS"],
        "id": uuid.UUID("42367f86-be47-4cca-865f-fb8ca721aa98"),
        "polygon": STIS_COS_SAA_POLYGON,
    },
    {
        "instrument_names": ["IXPE", "GBM", "LAT"],
        "id": uuid.UUID("79105b56-a99b-493d-9048-0eef3c07b258"),
        "polygon": FERMI_IXPE_SAA_POLYGON,
    },
    {
        "instrument_names": ["XTI"],
        "id": uuid.UUID("ae92f8e0-5b6b-4e6f-aeff-6b29f293437f"),
        "polygon": NICER_SAA_POLYGON,
    },
]


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    for instrument_info in INSTRUMENT_POLYGONS:
        saa_constraint = models.Constraint(
            id=instrument_info["id"],
            constraint_type=ConstraintType.SAA,
            constraint_parameters=SAAPolygonConstraint(
                polygon=instrument_info["polygon"]
            ).model_dump(),
        )
        session.add(saa_constraint)

        for instrument_name in instrument_info["instrument_names"]:
            instrument = (
                session.query(models.Instrument)
                .where(models.Instrument.short_name == instrument_name)
                .first()
            )

            if instrument is not None:
                instrument.constraints.extend([saa_constraint])
                session.add(instrument)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    for instrument_info in INSTRUMENT_POLYGONS:
        saa_constraint = (
            session.query(models.Constraint)
            .where(models.Constraint.id == instrument_info["id"])
            .first()
        )

        if saa_constraint is not None:
            for instrument_name in instrument_info["instrument_names"]:
                instrument = (
                    session.query(models.Instrument)
                    .where(models.Instrument.short_name == instrument_name)
                    .first()
                )

                if instrument is not None:
                    instrument.constraints.remove(saa_constraint)
                    session.add(instrument)

            session.delete(saa_constraint)

    session.commit()
