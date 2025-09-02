"""Add schedule_cadence to telescope table

Revision ID: d829f34da2f8
Revises: 0f1706aa008d
Create Date: 2025-08-28 14:21:46.218560

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm, update

import migrations.versions.model_snapshots.models_2025_09_02 as models

# revision identifiers, used by Alembic.
revision: str = "d829f34da2f8"
down_revision: Union[str, None] = "0f1706aa008d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        table_name="telescope",
        column=sa.Column("schedule_cadence", sa.String(length=50), nullable=True),
        schema="across",
    )

    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    # Fermi
    # LAT planned runs as an independent task from GBM
    # GBM does not yet have an ingestion task
    op.execute(
        update(models.Telescope)
        .where(
            models.Telescope.id.in_(
                [
                    # LAT
                    uuid.UUID("222d5f4a-8fd6-4299-a696-b3a6cb13d7bc")
                ]
            )
        )
        .values(schedule_cadence="22 2 * * *")
    )

    # TESS
    op.execute(
        update(models.Telescope)
        .where(
            models.Telescope.id.in_([uuid.UUID("653e6456-2cb0-49da-a6be-7c7ed69c0cb5")])
        )
        .values(schedule_cadence="12 22 * 8 *")
    )

    # Chandra
    op.execute(
        update(models.Telescope)
        .where(
            models.Telescope.id.in_([uuid.UUID("310a569b-3280-48e7-9a53-1e2f2a88565f")])
        )
        .values(schedule_cadence="13 2 * * 2")
    )

    # Swift
    # All swift telescopes are ingested at the same time in one task, so they can all have the same schedule cadence
    op.execute(
        update(models.Telescope)
        .where(
            models.Telescope.id.in_(
                [
                    # Swift_XRT
                    uuid.UUID("4994a365-428f-40ce-92ae-64393b8b565a"),
                    # Swift_UVOT
                    uuid.UUID("a17fb486-a194-4354-8c4c-f7582fd790bc"),
                    # Swift_BAT
                    uuid.UUID("c4249d8b-f5aa-43fb-9c46-aaa9b503c446"),
                ]
            )
        )
        .values(schedule_cadence="44 22 * * *")
    )

    # JWST
    op.execute(
        update(models.Telescope)
        .where(
            models.Telescope.id.in_([uuid.UUID("225ad468-585f-4f5e-8b64-09a4adfa1b7d")])
        )
        .values(schedule_cadence="33 22 * * *")
    )

    # HST
    op.execute(
        update(models.Telescope)
        .where(
            models.Telescope.id.in_([uuid.UUID("d8af2063-1a11-4941-aa06-2d63a9d9b918")])
        )
        .values(schedule_cadence="59 22 * * *")
    )

    # XMM
    op.execute(
        update(models.Telescope)
        .where(
            models.Telescope.id.in_([uuid.UUID("f2ae30ec-cd64-41b1-a951-4da29aa9f4ab")])
        )
        .values(schedule_cadence="0 1,9,17 * * *")
    )

    # IXPE
    op.execute(
        update(models.Telescope)
        .where(
            models.Telescope.id.in_([uuid.UUID("be6eeadc-9b7c-481d-81bd-4d1314dc0d49")])
        )
        .values(schedule_cadence="29 0 * * 2")
    )

    session.commit()


def downgrade() -> None:
    op.drop_column(
        table_name="telescope", column_name="schedule_cadence", schema="across"
    )
