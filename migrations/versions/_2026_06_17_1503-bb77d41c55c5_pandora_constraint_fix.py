"""pandora constraint fix

Revision ID: bb77d41c55c5
Revises: 572f3bb912a2
Create Date: 2026-06-17 15:03:44.853744

"""

from typing import Sequence, Union

from across.tools.visibility.constraints import (
    EarthLimbConstraint,
    MoonAngleConstraint,
    SunAngleConstraint,
)
from alembic import op
from sqlalchemy import orm, update

import migrations.versions.model_snapshots.models_2026_05_26 as models

# revision identifiers, used by Alembic.
revision: str = "bb77d41c55c5"
down_revision: Union[str, None] = "572f3bb912a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Update the Pandora constraints to have the correct parameter format.

    The previous parameters were not in the correct format and caused errors when trying to use the visibility calculator.
    """
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    sun_angle_update = (
        update(models.Constraint)
        .where(models.Constraint.id == "86398a06-4d2c-4765-aece-be1697cefd82")
        .values(constraint_parameters=SunAngleConstraint(min_angle=90).model_dump())  # type: ignore
    )
    earth_limb_update = (
        update(models.Constraint)
        .where(models.Constraint.id == "9429b370-c6c1-4a14-afac-6040de3f9bbe")
        .values(constraint_parameters=EarthLimbConstraint(min_angle=20).model_dump())
    )
    moon_angle_update = (
        update(models.Constraint)
        .where(models.Constraint.id == "0d417d1c-50b8-4c35-8d12-ab4b3a93c851")
        .values(constraint_parameters=MoonAngleConstraint(min_angle=40).model_dump())
    )
    session.execute(sun_angle_update)
    session.execute(earth_limb_update)
    session.execute(moon_angle_update)
    session.commit()


def downgrade() -> None:
    """Downgrade is not supported for this migration as the previous constraint parameters were bad"""
    pass
