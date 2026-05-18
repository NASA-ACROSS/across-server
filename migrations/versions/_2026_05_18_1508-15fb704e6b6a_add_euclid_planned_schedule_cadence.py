"""add Euclid planned schedule cadence

Revision ID: 15fb704e6b6a
Revises: d7412770b0be
Create Date: 2026-05-18 15:08:30.207420

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import delete, insert, orm

import migrations.versions.model_snapshots.models_2026_04_21 as models

# revision identifiers, used by Alembic.
revision: str = "15fb704e6b6a"
down_revision: Union[str, None] = "d7412770b0be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    op.execute(
        insert(models.ScheduleCadence).values(
            **{
                "id": "1c295d34-23fe-4a1e-ba03-af98029d6e0b",
                "telescope_id": "6f80ed81-bc0a-470f-a4dd-16db130911cb",
                "cron": "56 2 * * 2",
                "schedule_status": "planned",
            }
        )
    )

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    op.execute(
        delete(models.ScheduleCadence).where(
            models.ScheduleCadence.id == "1c295d34-23fe-4a1e-ba03-af98029d6e0b"
        )
    )

    session.commit()
