"""Add schedule_cadence to telescope table

Revision ID: d829f34da2f8
Revises: 0f1706aa008d
Create Date: 2025-08-28 14:21:46.218560

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import insert, orm

import migrations.versions.model_snapshots.models_2025_09_02 as models

# revision identifiers, used by Alembic.
revision: str = "d829f34da2f8"
down_revision: Union[str, None] = "0f1706aa008d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "schedule_cadence",
        sa.Column("telescope_id", sa.UUID(), nullable=False),
        sa.Column("schedule_status", sa.String(length=50), nullable=False),
        sa.Column("cron", sa.String(length=50), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column("modified_by_id", sa.UUID(), nullable=True),
        sa.Column("modified_on", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["telescope_id"],
            ["across.telescope.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="across",
    )
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    schedule_cadences = [
        {  # Fermi
            # LAT planned runs as an independent task from GBM
            "telescope_id": "222d5f4a-8fd6-4299-a696-b3a6cb13d7bc",
            "cron": "22 2 * * *",
            "schedule_status": "planned",
        },
        {  # Fermi
            # GBM does not yet have an ingestion task
            "telescope_id": "6fd90826-c3c9-4ad0-be01-63ed88a8f484",
            "cron": "27 2 * * *",
            "schedule_status": "planned",
        },
        {  # TESS
            "telescope_id": "653e6456-2cb0-49da-a6be-7c7ed69c0cb5",
            "cron": "12 22 * 8 *",
            "schedule_status": "planned",
        },
        {  # Chandra
            "telescope_id": "310a569b-3280-48e7-9a53-1e2f2a88565f",
            "cron": "13 2 * * 2",
            "schedule_status": "planned",
        },
        {  # Swift_XRT
            "telescope_id": "4994a365-428f-40ce-92ae-64393b8b565a",
            "cron": "44 22 * * *",
            "schedule_status": "planned",
        },
        {  # Swift_UVOT
            "telescope_id": "a17fb486-a194-4354-8c4c-f7582fd790bc",
            "cron": "44 22 * * *",
            "schedule_status": "planned",
        },
        {  # Swift_BAT
            "telescope_id": "c4249d8b-f5aa-43fb-9c46-aaa9b503c446",
            "cron": "44 22 * * *",
            "schedule_status": "planned",
        },
        {  # JWST
            "telescope_id": "225ad468-585f-4f5e-8b64-09a4adfa1b7d",
            "cron": "33 22 * * *",
            "schedule_status": "planned",
        },
        {  # HST
            "telescope_id": "d8af2063-1a11-4941-aa06-2d63a9d9b918",
            "cron": "59 22 * * *",
            "schedule_status": "planned",
        },
        {  # XMM
            "telescope_id": "f2ae30ec-cd64-41b1-a951-4da29aa9f4ab",
            "cron": "0 1,9,17 * * *",
            "schedule_status": "planned",
        },
        {  # IXPE
            "telescope_id": "be6eeadc-9b7c-481d-81bd-4d1314dc0d49",
            "cron": "29 0 * * 2",
            "schedule_status": "planned",
        },
        {  # NuStar
            "telescope_id": "281a5a5d-3629-4aa3-a739-968bee65415f",
            "cron": "7 1 * * *",
            "schedule_status": "planned",
        },
        {  # NuStar performed
            "telescope_id": "281a5a5d-3629-4aa3-a739-968bee65415f",
            "cron": "53 2 * * 2",
            "schedule_status": "performed",
        },
        {  # NICER
            "telescope_id": "8ca37c8a-8fcc-404b-a58d-a9854099c97d",
            "cron": "18 23 * * *",
            "schedule_status": "planned",
        },
    ]

    for cadence in schedule_cadences:
        op.execute(insert(models.ScheduleCadence).values(**cadence))

    session.commit()


def downgrade() -> None:
    op.drop_table("schedule_cadence", schema="across")
