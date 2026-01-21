"""soft delete users

Revision ID: effbd9073baa
Revises: 9032acd18e5d
Create Date: 2026-01-08 13:12:01.309615

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm, select

import migrations.versions.model_snapshots.models_2026_01_08 as models

# revision identifiers, used by Alembic.
revision: str = "effbd9073baa"
down_revision: Union[str, None] = "9032acd18e5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: add nullable column
    op.add_column(
        table_name="user",
        column=sa.Column("is_deleted", sa.Boolean(), nullable=True),
        schema="across",
    )

    # Step 2: populate column with values
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    users = session.scalars(select(models.User).with_for_update())
    for user in list(users.all()):
        user.is_deleted = False

    session.commit()

    # Step 3: set column to not nullable.
    op.alter_column(
        table_name="user", column_name="is_deleted", nullable=False, schema="across"
    )


def downgrade() -> None:
    op.drop_column(table_name="user", column_name="is_deleted", schema="across")
