"""add lsstcam visibility type

Revision ID: 00b3a6244b1c
Revises: 7774f10e57fb
Create Date: 2026-02-20 16:38:35.357648

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm, update

import migrations.versions.model_snapshots.models_2026_02_13 as models
from across_server.core.enums.visibility_type import VisibilityType

# revision identifiers, used by Alembic.
revision: str = "00b3a6244b1c"
down_revision: Union[str, None] = "7774f10e57fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LSSTCAM_INSTRUMENT_UUID = "b9342e4c-1106-4e47-a434-30c639ce661b"


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    session.execute(
        update(models.Instrument)
        .where(models.Instrument.id == LSSTCAM_INSTRUMENT_UUID)
        .values(visibility_type=VisibilityType.EPHEMERIS)
    )

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    session.execute(
        update(models.Instrument)
        .where(models.Instrument.id == LSSTCAM_INSTRUMENT_UUID)
        .values(visibility_type=None)
    )

    session.commit()
