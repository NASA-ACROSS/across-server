"""add observation_strategy column to instrument table

Revision ID: 548789dd23d9
Revises: cc55dd06ba45
Create Date: 2026-02-13 09:45:38.878644

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm, select

import migrations.versions.model_snapshots.models_2026_02_13 as models
from across_server.core.enums.observation_strategy import ObservationStrategy

# revision identifiers, used by Alembic.
revision: str = "548789dd23d9"
down_revision: Union[str, None] = "cc55dd06ba45"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SURVEY_INSTRUMENT_SHORT_NAMES = ["TESS", "LAT", "GBM", "LSSTCam", "Swift_BAT"]


def upgrade() -> None:
    # Step 1: add nullable column
    op.add_column(
        "instrument",
        sa.Column("observation_strategy", sa.String(), nullable=True),
        schema="across",
    )

    # Step 2: populate column with values
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    instruments = session.scalars(select(models.Instrument).with_for_update())

    for instrument in list(instruments.all()):
        if instrument.short_name in SURVEY_INSTRUMENT_SHORT_NAMES:
            instrument.observation_strategy = ObservationStrategy.SURVEY
        else:
            instrument.observation_strategy = ObservationStrategy.POINTED

    session.commit()

    # Step 3: set column to not nullable.
    op.alter_column(
        "instrument", "observation_strategy", nullable=False, schema="across"
    )


def downgrade() -> None:
    op.drop_column("instrument", "observation_strategy", schema="across")
