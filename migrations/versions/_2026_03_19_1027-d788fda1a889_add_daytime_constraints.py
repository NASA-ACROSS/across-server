"""add daytime constraints

Revision ID: d788fda1a889
Revises: 548789dd23d9
Create Date: 2026-03-19 10:27:21.906028

"""

import uuid
from typing import Sequence, Union

from across.tools.core.enums import ConstraintType, TwilightType
from across.tools.visibility.constraints import DaytimeConstraint
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_02_23 as models

# revision identifiers, used by Alembic.
revision: str = "d788fda1a889"
down_revision: Union[str, None] = "548789dd23d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

"""
Both Keck telescopes and LSST begin normal science operations
at the start of astronomical twilight. While they sometimes
observe certain objects during nautical twilight, namely
near-Earth objects, these observations are typically conducted
under specific proposals or surveys. Therefore for the purposes
of visibility calculations we should assume objects are constrained
before astronomical twilight.
"""
GROUND_BASED_TELESCOPE_NAMES = ["Keck I", "Keck II", "LSST"]


def upgrade() -> None:
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


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    astronomical_twilight_constraint = (
        session.query(models.Constraint)
        .where(models.Constraint.id == "7b737872-4b99-4fbe-b367-09a986b4cfdc")
        .first()
    )

    session.delete(astronomical_twilight_constraint)
    session.commit()
