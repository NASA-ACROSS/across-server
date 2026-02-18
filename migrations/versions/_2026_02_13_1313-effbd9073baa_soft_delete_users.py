"""soft delete users

Revision ID: effbd9073baa
Revises: cc55dd06ba45
Create Date: 2026-02-13 13:13:01.309615

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm, select

import migrations.versions.model_snapshots.models_2026_02_13 as models

# revision identifiers, used by Alembic.
revision: str = "effbd9073baa"
down_revision: Union[str, None] = "cc55dd06ba45"
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

    # index to speed up queries for is_deleted
    op.create_index(
        "ix_user_is_deleted",
        "user",
        ["is_deleted"],
        unique=False,
        schema="across",
    )


def downgrade() -> None:
    op.drop_index("ix_user_is_deleted", table_name="user", schema="across")
    op.drop_column(table_name="user", column_name="is_deleted", schema="across")
