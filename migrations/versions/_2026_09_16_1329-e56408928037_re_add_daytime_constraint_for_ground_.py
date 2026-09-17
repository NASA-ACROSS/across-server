"""re-add-daytime-constraint-for-ground-observatories

Revision ID: e56408928037
Revises: dd08ad0df8af
Create Date: 2026-09-16 13:29:38.008544

"""

import uuid
from typing import Sequence, Union

from across.tools.core.enums import ConstraintType, TwilightType
from across.tools.visibility.constraints import DaytimeConstraint
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_05_26 as models

# revision identifiers, used by Alembic.
revision: str = "e56408928037"
down_revision: Union[str, None] = "dd08ad0df8af"
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
LSST_TELESCOPE_ID = "d18710e4-2a21-4dc6-8a57-eff0f46fc5f7"
KECK1_TELESCOPE_ID = "bb811891-76d6-476d-9141-430c6ef5830d"
KECK2_TELESCOPE_ID = "74c41e48-5428-4c7a-a16c-6e47e2a7a484"
GROUND_BASED_TELESCOPE_IDS = [LSST_TELESCOPE_ID, KECK1_TELESCOPE_ID, KECK2_TELESCOPE_ID]


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
    for telescope_id in GROUND_BASED_TELESCOPE_IDS:
        telescope = (
            session.query(models.Telescope)
            .where(models.Telescope.id == telescope_id)
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
