"""fix HST sun angle constraint

Revision ID: dd08ad0df8af
Revises: 5e170132081b
Create Date: 2026-08-10 18:15:14.809021

"""

import uuid
from typing import Sequence, Union

from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import SunAngleConstraint
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_05_26 as models

# revision identifiers, used by Alembic.
revision: str = "dd08ad0df8af"
down_revision: Union[str, None] = "5e170132081b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# The minimum sun angle for HST in single gyro mode is 62.5 degrees, as per the HST documentation:
# https://www.stsci.edu/files/live/sites/www/files/home/hst/observing/_documents/HST-RGM-Primer.pdf
HST_SINGLE_GYRO_MODE_MIN_SUN_ANGLE = 62.5


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    hst_sun_angle_constraint = models.Constraint(
        id=uuid.UUID("ee3758c5-2a58-4c90-bf1d-1dac33daff63"),
        constraint_type=ConstraintType.SUN,
        constraint_parameters=SunAngleConstraint(
            min_angle=HST_SINGLE_GYRO_MODE_MIN_SUN_ANGLE,
        ).model_dump(),
    )
    session.add(hst_sun_angle_constraint)
    session.flush()

    hst_telescope = (
        session.query(models.Telescope)
        .where(models.Telescope.short_name == "HST")
        .one()
    )

    for instrument in hst_telescope.instruments:
        for constraint in instrument.constraints:
            if constraint.constraint_type == ConstraintType.SUN.value:
                instrument.constraints.remove(constraint)

        instrument.constraints.append(hst_sun_angle_constraint)
        session.add(instrument)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    hst_sun_angle_constraint = (
        session.query(models.Constraint)
        .where(models.Constraint.id == "ee3758c5-2a58-4c90-bf1d-1dac33daff63")
        .one()
    )

    old_sun_angle_constraint = (
        session.query(models.Constraint)
        .where(models.Constraint.id == "d530a37d-0fc1-4ea3-8bae-1ab4940308b5")
        .one()
    )

    hst_telescope = (
        session.query(models.Telescope)
        .where(models.Telescope.short_name == "HST")
        .one()
    )

    for instrument in hst_telescope.instruments:
        for constraint in instrument.constraints:
            if constraint.id == hst_sun_angle_constraint.id:
                instrument.constraints.remove(constraint)

        instrument.constraints.append(old_sun_angle_constraint)
        session.add(instrument)

    session.delete(hst_sun_angle_constraint)
    session.commit()
