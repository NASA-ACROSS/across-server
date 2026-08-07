"""fix jwst constraints

Revision ID: cb5340af20da
Revises: 56f11c079a8b
Create Date: 2026-08-05 19:30:21.000000

"""

import uuid
from collections.abc import Sequence

from across.tools.core.enums import ConstraintType
from across.tools.visibility.constraints import SunAngleConstraint
from alembic import op
from sqlalchemy import orm, select

import migrations.versions.model_snapshots.models_2026_05_26 as models

# revision identifiers, used by Alembic.
revision: str = "cb5340af20da"
down_revision: str | None = "56f11c079a8b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# JWST instruments, from the original JWST observatory migration (2c08825167f4)
JWST_INSTRUMENT_IDS = [
    uuid.UUID("d21c66bc-7173-454e-8f67-69df1b43590d"),  # JWST_MIRI
    uuid.UUID("9899d36c-9e07-4927-8295-04c4ced70f1a"),  # JWST_NIRCAM
    uuid.UUID("905bd0aa-6be2-43a1-b1d3-bb8df1632ac8"),  # JWST_NIRISS
    uuid.UUID("1e1b0263-7e49-4c00-985a-568927353700"),  # JWST_NIRSPEC
]

# The generic constraints applied to every pointed instrument by migration
# 50c390eb41cb. These rows are shared, so they must not be modified or deleted
# here - JWST is only detached from them.
GENERIC_SUN_45_CONSTRAINT_ID = uuid.UUID("d530a37d-0fc1-4ea3-8bae-1ab4940308b5")
GENERIC_MOON_20_CONSTRAINT_ID = uuid.UUID("3390c3f9-62ea-4ee1-a94e-cc5178a7a383")
GENERIC_EARTH_20_CONSTRAINT_ID = uuid.UUID("70d3f9cb-2550-4064-9808-36a75f9cae87")

JWST_SUN_CONSTRAINT_ID = uuid.UUID("f0a1c4d2-6b3e-4a58-9d21-7c5e8b0a3f14")

# JWST's field of regard is a pitch angle of 85 - 135 degrees from the Sun: the
# sunshield fixes how far the telescope can be tilted towards the Sun (85 deg)
# and towards the anti-Sun direction (135 deg).
# https://jwst-docs.stsci.edu/jwst-observatory-characteristics/jwst-observatory-coordinate-system-and-field-of-regard
JWST_SUN_MIN_ANGLE = 85.0
JWST_SUN_MAX_ANGLE = 135.0

# Constraint types removed from JWST, see the upgrade() docstring.
REMOVED_CONSTRAINT_TYPES = {
    ConstraintType.SUN.value,
    ConstraintType.MOON.value,
    ConstraintType.EARTH.value,
}


def upgrade() -> None:
    """
    Replace the JWST instrument constraints with the real field of regard.

    JWST was picking up the generic pointed-instrument constraints - a 45
    degree Sun angle, a 20 degree Moon angle and a 20 degree Earth limb - none
    of which describe an observatory at L2.

    The Sun constraint becomes JWST's actual field of regard, a pitch angle of
    85 - 135 degrees. The generic one both allowed pointings far closer to the
    Sun than the sunshield permits, and had no anti-Sun limit at all.

    The Moon and Earth limb constraints are dropped rather than corrected. Seen
    from L2 the Earth lies within roughly 30 degrees of the Sun and the Moon
    within roughly 45 degrees, so both are permanently buried inside the 85
    degree Sun exclusion and can never be the binding constraint. Keeping them
    only risks spurious exclusions if the ephemeris position is off, since
    EarthLimbConstraint scales its exclusion by the spacecraft-Earth distance.
    This matches Euclid, also at L2, which is modelled with a Sun constraint
    alone (6435266af272).
    """
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    jwst_sun_constraint = models.Constraint(
        id=JWST_SUN_CONSTRAINT_ID,
        constraint_type=ConstraintType.SUN.value,
        constraint_parameters=SunAngleConstraint(
            min_angle=JWST_SUN_MIN_ANGLE,
            max_angle=JWST_SUN_MAX_ANGLE,
        ).model_dump(),
    )
    session.add(jwst_sun_constraint)

    instruments = session.scalars(
        select(models.Instrument).where(models.Instrument.id.in_(JWST_INSTRUMENT_IDS))
    ).all()

    for instrument in instruments:
        # Detach from the shared generic constraints rather than deleting them,
        # then attach the JWST specific Sun constraint.
        instrument.constraints = [
            constraint
            for constraint in instrument.constraints
            if constraint.constraint_type not in REMOVED_CONSTRAINT_TYPES
        ] + [jwst_sun_constraint]
        session.add(instrument)

    session.commit()


def downgrade() -> None:
    """Put the JWST instruments back on the generic pointed-instrument constraints."""
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    generic_constraints = session.scalars(
        select(models.Constraint).where(
            models.Constraint.id.in_(
                [
                    GENERIC_SUN_45_CONSTRAINT_ID,
                    GENERIC_MOON_20_CONSTRAINT_ID,
                    GENERIC_EARTH_20_CONSTRAINT_ID,
                ]
            )
        )
    ).all()

    instruments = session.scalars(
        select(models.Instrument).where(models.Instrument.id.in_(JWST_INSTRUMENT_IDS))
    ).all()

    for instrument in instruments:
        instrument.constraints = [
            constraint
            for constraint in instrument.constraints
            if constraint.id != JWST_SUN_CONSTRAINT_ID
        ] + list(generic_constraints)
        session.add(instrument)

    session.flush()

    jwst_sun_constraint = session.get(models.Constraint, JWST_SUN_CONSTRAINT_ID)
    if jwst_sun_constraint is not None:
        session.delete(jwst_sun_constraint)

    session.commit()
