"""fix nustar constraint values and observatory parameters

Revision ID: de59d8935dbb
Revises: 842f5166cdfb
Create Date: 2026-11-05 13:41:40.157320

"""

import uuid
from datetime import datetime
from typing import Sequence, Union

from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import MoonAngleConstraint, SunAngleConstraint
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_05_26 as models
from across_server.core.enums import InstrumentType

# revision identifiers, used by Alembic.
revision: str = "de59d8935dbb"
down_revision: Union[str, None] = "842f5166cdfb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NUSTAR_OBSERVATORY_ID = "afc0ceca-bc57-4d38-a846-c5c36d62256a"
DEFAULT_CONSTRAINT_IDS = [
    "d530a37d-0fc1-4ea3-8bae-1ab4940308b5",
    "3390c3f9-62ea-4ee1-a94e-cc5178a7a383",
    "5a2bcefc-f08e-4d4f-a2a9-1dd526638884",
]


def upgrade() -> None:
    """
    Update NuSTAR's Sun and Moon angle constraint values, remove its
    Earth limb constraint, and update other observatory parameters.
    These new values reflect the ground truth as given to us by the NuSTAR team.
    """
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    nustar_sun_constraint = models.Constraint(
        id=uuid.UUID("01882516-7d64-457b-b81f-25d2ba98f8d0"),
        constraint_type=ConstraintType.SUN,
        constraint_parameters=SunAngleConstraint(
            min_angle=60,
            max_angle=130,
        ).model_dump(),
    )

    nustar_moon_constraint = models.Constraint(
        id=uuid.UUID("9a8743a9-73cb-473d-8aa2-8cc1a680ef7d"),
        constraint_type=ConstraintType.MOON,
        constraint_parameters=MoonAngleConstraint(
            min_angle=14,
        ).model_dump(),
    )

    session.add_all([nustar_sun_constraint, nustar_moon_constraint])

    observatory = (
        session.query(models.Observatory)
        .where(models.Observatory.id == NUSTAR_OBSERVATORY_ID)
        .first()
    )

    if observatory is not None:
        # Add NuSTAR operational begin date
        observatory.operational_begin_date = datetime(2012, 7, 1)

        session.add(observatory)

        for telescope in observatory.telescopes:
            if telescope is not None:
                for instrument in telescope.instruments:
                    if instrument is not None:
                        # Replace NuSTAR instrument constraints with the new ones
                        instrument.constraints = [
                            nustar_sun_constraint,
                            nustar_moon_constraint,
                        ]
                        # Update instrument type
                        instrument.type = InstrumentType.XRAY_IMAGING_SPECTROMETER
                        session.add(instrument)

    session.commit()


def downgrade() -> None:
    """Delete newly added constraints and revert back to old ones"""
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    nustar_constraints = (
        session.query(models.Constraint)
        .where(
            models.Constraint.id.in_(
                [
                    "01882516-7d64-457b-b81f-25d2ba98f8d0",
                    "9a8743a9-73cb-473d-8aa2-8cc1a680ef7d",
                ]
            )
        )
        .all()
    )

    if nustar_constraints is not None:
        for constraint in nustar_constraints:
            session.delete(constraint)

    # Reset the old constraints
    old_constraints = (
        session.query(models.Constraint)
        .where(models.Constraint.id.in_(DEFAULT_CONSTRAINT_IDS))
        .all()
    )
    observatory = (
        session.query(models.Observatory)
        .where(models.Observatory.id == NUSTAR_OBSERVATORY_ID)
        .first()
    )
    if observatory is not None:
        for telescope in observatory.telescopes:
            if telescope is not None:
                for instrument in telescope.instruments:
                    if instrument is not None:
                        # Replace NuSTAR instrument constraints with the new ones
                        instrument.constraints = old_constraints
                        session.add(instrument)

    session.commit()
