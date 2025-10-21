"""add SAA constraint

Revision ID: 9032acd18e5d
Revises: 50c390eb41cb
Create Date: 2025-10-21 14:02:27.152104

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
down_revision: Union[str, None] = "50c390eb41cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SAA_POLYGON = Polygon(
    [
        (39.0, -30.0),
        (36.0, -26.0),
        (28.0, -21.0),
        (6.0, -12.0),
        (-5.0, -6.0),
        (-21.0, 2.0),
        (-30.0, 3.0),
        (-45.0, 2.0),
        (-60.0, -2.0),
        (-75.0, -7.0),
        (-83.0, -10.0),
        (-87.0, -16.0),
        (-86.0, -23.0),
        (-83.0, -30.0),
    ]
)

SAA_AFFECTED_OBS_NAMES = [
    "Swift",
    "HST",
    "IXPE",
    "Fermi",
    "NuSTAR",
    "NICER",
]


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    saa_constraint = models.Constraint(
        id=uuid.UUID("ae3506a5-d51f-4bfa-bc79-4f848f257ac6"),
        constraint_type=ConstraintType.SAA,
        constraint_parameters=SAAPolygonConstraint(polygon=SAA_POLYGON).model_dump(),
    )
    session.add(saa_constraint)

    saa_affected_observatories = (
        session.query(models.Observatory)
        .where(models.Observatory.short_name.in_(SAA_AFFECTED_OBS_NAMES))
        .all()
    )

    for observatory in saa_affected_observatories:
        for telescope in observatory.telescopes:
            for instrument in telescope.instruments:
                instrument.constraints.extend([saa_constraint])
                session.add(instrument)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    saa_affected_observatories = (
        session.query(models.Observatory)
        .where(models.Observatory.short_name.in_(SAA_AFFECTED_OBS_NAMES))
        .all()
    )

    saa_constraint = (
        session.query(models.Constraint)
        .where(
            models.Constraint.id == uuid.UUID("ae3506a5-d51f-4bfa-bc79-4f848f257ac6")
        )
        .first()
    )

    if saa_constraint is not None:
        for observatory in saa_affected_observatories:
            for telescope in observatory.telescopes:
                for instrument in telescope.instruments:
                    instrument.constraints.remove(saa_constraint)
                    session.add(instrument)

    session.delete(saa_constraint)
    session.commit()
