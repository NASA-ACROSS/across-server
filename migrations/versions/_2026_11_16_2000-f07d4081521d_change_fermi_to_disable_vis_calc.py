"""change fermi to disable vis calc

Revision ID: f07d4081521d
Revises: b9d29367730c
Create Date: 2026-11-16 16:47:50.975115

"""

import uuid
from collections.abc import Sequence

from alembic import op
from sqlalchemy import false, orm, select

import migrations.versions.model_snapshots.models_2026_11_17 as models

# revision identifiers, used by Alembic.
revision: str = "f07d4081521d"
down_revision: str | None = "b9d29367730c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

vis_calc_setting = models.Setting(
    id=uuid.UUID("43acc91f-ca17-43e3-97b2-115050775335"),
    name="is_visibility_calculator_enabled",
    display_name="Visibility Calculator Enabled",
    description="Enable or disable the visibility calculator for this instrument.",
    type="boolean",
)


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # Create Setting for vis calc
    session.add(vis_calc_setting)

    instruments = session.scalars(
        select(models.Instrument)
        .join(models.Telescope)
        .join(models.Observatory)
        .where(models.Observatory.name.contains("Fermi"))
    ).all()

    for instrument in instruments:
        setting = models.InstrumentSetting(
            instrument_id=instrument.id,
            setting_id=vis_calc_setting.id,
            value=false(),
        )
        session.add(setting)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    setting = session.get(models.Setting, vis_calc_setting.id)

    # Remove Setting for vis calc
    session.delete(setting)

    session.commit()
