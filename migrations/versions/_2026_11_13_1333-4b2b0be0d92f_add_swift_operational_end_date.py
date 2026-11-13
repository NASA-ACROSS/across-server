"""add Swift operational end date

Revision ID: 4b2b0be0d92f
Revises: 842f5166cdfb
Create Date: 2026-11-13 13:33:05.809971

"""

from datetime import datetime
from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2026_05_26 as models

# revision identifiers, used by Alembic.
revision: str = "4b2b0be0d92f"
down_revision: Union[str, None] = "842f5166cdfb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SWIFT_OBSERVATORY_UUID = "d5faadca-c0bb-4bb8-b4e4-75149b435ae8"


def upgrade() -> None:
    """
    Add operational_end_date for the Swift observatory, and change is_operational to False
    for the observatory, its telescopes, and its instruments.
    """
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    swift_observatory = (
        session.query(models.Observatory)
        .where(models.Observatory.id == SWIFT_OBSERVATORY_UUID)
        .first()
    )
    if swift_observatory is not None:
        swift_observatory.operational_end_date = datetime(2026, 10, 20, 23, 59, 59)
        swift_observatory.is_operational = False
        session.add(swift_observatory)

        for telescope in swift_observatory.telescopes:
            telescope.is_operational = False
            session.add(telescope)

            for instrument in telescope.instruments:
                instrument.is_operational = False
                session.add(instrument)

    session.commit()


def downgrade() -> None:
    """
    Remove operational_end_date from Swift observatory and change is_operaitonal to True
    for the observatory, its telescopes, and its instruments.
    """
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    swift_observatory = (
        session.query(models.Observatory)
        .where(models.Observatory.id == SWIFT_OBSERVATORY_UUID)
        .first()
    )
    if swift_observatory is not None:
        swift_observatory.operational_end_date = None
        swift_observatory.is_operational = True
        session.add(swift_observatory)

        for telescope in swift_observatory.telescopes:
            telescope.is_operational = True
            session.add(telescope)

            for instrument in telescope.instruments:
                instrument.is_operational = True
                session.add(instrument)

    session.commit()
