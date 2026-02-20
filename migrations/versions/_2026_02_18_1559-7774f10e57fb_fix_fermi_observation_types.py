"""fix fermi observation types

Revision ID: 7774f10e57fb
Revises: 59e4b9fd7386
Create Date: 2026-02-18 15:59:54.013426

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm, update

import migrations.versions.model_snapshots.models_2026_02_13 as models
from across_server.core.enums import ObservationType

# revision identifiers, used by Alembic.
revision: str = "7774f10e57fb"
down_revision: Union[str, None] = "59e4b9fd7386"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FERMI_LAT_INSTRUMENT_UUID = "7f7b97ed-e341-476f-908b-7bad8740b31b"


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    # Update observation data
    session.execute(
        update(models.Observation)
        .where(models.Observation.instrument_id == FERMI_LAT_INSTRUMENT_UUID)
        .values(type=ObservationType.SLEW)
    )

    session.commit()


def downgrade() -> None:
    # Don't downgrade to old incorrect values, so do nothing
    pass
