"""add lsst schedule cadence

Revision ID: 59e4b9fd7386
Revises: effbd9073baa
Create Date: 2026-02-17 14:54:55.011830

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import delete, insert, orm

import migrations.versions.model_snapshots.models_2026_02_13 as models

# revision identifiers, used by Alembic.
revision: str = "59e4b9fd7386"
down_revision: Union[str, None] = "effbd9073baa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    cadence = {
        "id": "4c31238a-96cb-4035-b684-97375dcd5e03",
        "telescope_id": "d18710e4-2a21-4dc6-8a57-eff0f46fc5f7",
        "cron": "0 18 * * *",
        "schedule_status": "planned",
    }

    op.execute(insert(models.ScheduleCadence).values(**cadence))

    session.commit()


def downgrade() -> None:
    op.execute(
        delete(models.ScheduleCadence).where(
            models.ScheduleCadence.id == "4c31238a-96cb-4035-b684-97375dcd5e03"
        )
    )
