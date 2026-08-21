"""fix pandora earthlimb constraint

Revision ID: 9e16519fbb23
Revises: dd08ad0df8af
Create Date: 2026-08-21 11:41:18.498052

"""

from typing import Sequence, Union

from across.tools.visibility.constraints import DaytimeConstraint, EarthLimbConstraint
from alembic import op
from sqlalchemy import orm, update

import migrations.versions.model_snapshots.models_2026_05_26 as models

# revision identifiers, used by Alembic.
revision: str = "9e16519fbb23"
down_revision: Union[str, None] = "dd08ad0df8af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Update the Pandora earthlimb constraint
    """
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    compound_constraint = (EarthLimbConstraint(min_angle=45) & DaytimeConstraint()) | (
        EarthLimbConstraint(min_angle=9)
    )

    compound_earth_limb_update = (
        update(models.Constraint)
        .where(models.Constraint.id == "9429b370-c6c1-4a14-afac-6040de3f9bbe")
        .values(constraint_parameters=compound_constraint.model_dump())
    )
    session.execute(compound_earth_limb_update)
    session.commit()


def downgrade() -> None:
    """Downgrade is not supported for this migration as the previous constraint parameters were bad"""
    pass
