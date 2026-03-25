"""rollback daytime constraints

Revision ID: 1613a21d5d5f
Revises: d788fda1a889
Create Date: 2026-03-25 14:22:16.416765

"""

import uuid
from typing import Sequence, Union

from across.tools.core.enums import ConstraintType, TwilightType
from across.tools.visibility.constraints import DaytimeConstraint
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_02_23 as models

# revision identifiers, used by Alembic.
revision: str = "1613a21d5d5f"
down_revision: Union[str, None] = "d788fda1a889"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

GROUND_BASED_TELESCOPE_NAMES = ["Keck I", "Keck II", "LSST"]


def upgrade() -> None:
    """
    Rollback daytime constraints to avoid crash in client.
    """
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    astronomical_twilight_constraint = (
        session.query(models.Constraint)
        .where(models.Constraint.id == "7b737872-4b99-4fbe-b367-09a986b4cfdc")
        .first()
    )

    session.delete(astronomical_twilight_constraint)
    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    # Add astronomical twilight constraint
    astronomical_twilight_constraint = models.Constraint(
        id=uuid.UUID("7b737872-4b99-4fbe-b367-09a986b4cfdc"),
        constraint_type=ConstraintType.DAYTIME,
        constraint_parameters=DaytimeConstraint(
            twilight_type=TwilightType.ASTRONOMICAL
        ).model_dump(),
    )
    session.add(astronomical_twilight_constraint)

    # Add this constraint to relevant instruments
    for telescope_name in GROUND_BASED_TELESCOPE_NAMES:
        telescope = (
            session.query(models.Telescope)
            .where(models.Telescope.short_name == telescope_name)
            .first()
        )

        if telescope is not None:
            for instrument in telescope.instruments:
                instrument.constraints.extend([astronomical_twilight_constraint])
                session.add(instrument)

    session.commit()
