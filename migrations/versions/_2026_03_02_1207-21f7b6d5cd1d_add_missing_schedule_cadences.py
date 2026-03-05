"""add missing schedule cadences

Revision ID: 21f7b6d5cd1d
Revises: 90c0b855ecde
Create Date: 2026-03-02 12:07:55.276903

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import delete, insert, orm

import migrations.versions.model_snapshots.models_2026_02_13 as models

CADENCES = [
    # Chandra as-flown
    {
        "id": "51e6f6cc-5d1d-4964-843d-174173ac3216",
        "telescope_id": "310a569b-3280-48e7-9a53-1e2f2a88565f",
        "cron": "13 4 * * 7",
        "schedule_status": "performed",
    },
    # HST as-flown
    {
        "id": "32440959-8365-4c8a-a345-cc463e11e879",
        "telescope_id": "d8af2063-1a11-4941-aa06-2d63a9d9b918",
        "cron": "52 5 * * *",
        "schedule_status": "performed",
    },
    # Swift UVOT as-flown
    {
        "id": "7267480d-3fc2-46f4-9b22-d6b3cac8ca0e",
        "telescope_id": "a17fb486-a194-4354-8c4c-f7582fd790bc",
        "cron": "0 4 * * *",
        "schedule_status": "performed",
    },
    # Swift XRT as-flown
    {
        "id": "5429260c-326a-4648-a841-3ba10f79d0bb",
        "telescope_id": "4994a365-428f-40ce-92ae-64393b8b565a",
        "cron": "0 4 * * *",
        "schedule_status": "performed",
    },
    # Swift BAT as-flown
    {
        "id": "fff4fcfe-0c0f-4204-aa9f-207266d0b0bc",
        "telescope_id": "c4249d8b-f5aa-43fb-9c46-aaa9b503c446",
        "cron": "0 4 * * *",
        "schedule_status": "performed",
    },
]

# revision identifiers, used by Alembic.
revision: str = "21f7b6d5cd1d"
down_revision: Union[str, None] = "90c0b855ecde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    for cadence in CADENCES:
        op.execute(insert(models.ScheduleCadence).values(**cadence))

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    for cadence in CADENCES:
        op.execute(
            delete(models.ScheduleCadence).where(
                models.ScheduleCadence.id == cadence.get("id")
            )
        )

    session.commit()
