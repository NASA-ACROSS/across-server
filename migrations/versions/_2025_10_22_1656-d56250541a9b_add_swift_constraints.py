"""add Swift constraints

Revision ID: d56250541a9b
Revises: 161e7121bdbf
Create Date: 2025-10-22 16:56:46.238481

"""

import uuid
from typing import Sequence, Union

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

import migrations.versions.model_snapshots.models_2025_10_03 as models

# revision identifiers, used by Alembic.
revision: str = "d56250541a9b"
down_revision: Union[str, None] = "161e7121bdbf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SWIFT_SAA_POLYGON = Polygon(
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
        (39.0, -30.0),
    ]
)


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    swift_saa_constraint = models.Constraint(
        id=uuid.UUID("255efe87-6b02-4d9b-ae88-b21955202ef9"),
        constraint_type=ConstraintType.SAA,
        constraint_parameters=SAAPolygonConstraint(
            polygon=SWIFT_SAA_POLYGON
        ).model_dump(),
    )
    session.add(swift_saa_constraint)

    swift_sun_angle_constraint = models.Constraint(
        id=uuid.UUID("03f373d0-70df-46f6-836e-bf6d399fa503"),
        constraint_type=ConstraintType.SUN,
        constraint_parameters=SunAngleConstraint(
            min_angle=45, max_angle=170
        ).model_dump(),
    )
    session.add(swift_sun_angle_constraint)

    swift_moon_angle_constraint = models.Constraint(
        id=uuid.UUID("c27f3da2-3af1-461d-8298-104b41cc5fa1"),
        constraint_type=ConstraintType.MOON,
        constraint_parameters=MoonAngleConstraint(min_angle=21).model_dump(),
    )
    session.add(swift_moon_angle_constraint)

    swift_earth_limb_constraint = models.Constraint(
        id=uuid.UUID("10744cd8-8eb2-4bb9-b2f3-0a116d5508ef"),
        constraint_type=ConstraintType.EARTH,
        constraint_parameters=EarthLimbConstraint(min_angle=33).model_dump(),
    )
    session.add(swift_earth_limb_constraint)

    swift_observatory = (
        session.query(models.Observatory)
        .where(models.Observatory.short_name == "Swift")
        .all()[0]
    )
    for telescope in swift_observatory.telescopes:
        for instrument in telescope.instruments:
            instrument.constraints = [
                swift_sun_angle_constraint,
                swift_saa_constraint,
                swift_moon_angle_constraint,
                swift_earth_limb_constraint,
            ]
            session.add(instrument)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    generic_constraint_ids = [
        uuid.UUID("d530a37d-0fc1-4ea3-8bae-1ab4940308b5"),  # Sun45
        uuid.UUID("3390c3f9-62ea-4ee1-a94e-cc5178a7a383"),  # Moon20
        uuid.UUID("70d3f9cb-2550-4064-9808-36a75f9cae87"),  # Earth 20
    ]

    swift_constraint_ids = [
        uuid.UUID("255efe87-6b02-4d9b-ae88-b21955202ef9"),  # SAA
        uuid.UUID("03f373d0-70df-46f6-836e-bf6d399fa503"),  # Sun
        uuid.UUID("c27f3da2-3af1-461d-8298-104b41cc5fa1"),  # Moon
        uuid.UUID("10744cd8-8eb2-4bb9-b2f3-0a116d5508ef"),  # Earth
    ]
    generic_constraints = (
        session.query(models.Constraint)
        .where(models.Constraint.id.in_(generic_constraint_ids))
        .all()
    )

    swift_observatory = (
        session.query(models.Observatory)
        .where(models.Observatory.short_name == "Swift")
        .all()[0]
    )
    for telescope in swift_observatory.telescopes:
        for instrument in telescope.instruments:
            instrument.constraints = generic_constraints
            session.add(instrument)

    swift_constraints = (
        session.query(models.Constraint)
        .where(models.Constraint.id.in_(swift_constraint_ids))
        .all()
    )
    for constraint in swift_constraints:
        session.delete(constraint)

    session.commit()
