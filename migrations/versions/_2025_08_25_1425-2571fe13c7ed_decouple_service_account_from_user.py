"""Decouple service_account from user

Revision ID: 2571fe13c7ed
Revises: 826bca5cbc49
Create Date: 2025-08-08 09:25:15.348983

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2571fe13c7ed"
down_revision: Union[str, None] = "826bca5cbc49"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_service_account",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("service_account_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["service_account_id"],
            ["across.service_account.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["across.user.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "service_account_id"),
        sa.UniqueConstraint("service_account_id", name="uq_service_account_id"),
        schema="across",
    )
    op.drop_constraint(
        "service_account_user_id_fkey",
        "service_account",
        schema="across",
        type_="foreignkey",
    )
    op.drop_column("service_account", "user_id", schema="across")


def downgrade() -> None:
    op.add_column(
        "service_account",
        sa.Column("user_id", sa.UUID(), autoincrement=False, nullable=False),
        schema="across",
    )
    op.create_foreign_key(
        "service_account_user_id_fkey",
        "service_account",
        "user",
        ["user_id"],
        ["id"],
        source_schema="across",
        referent_schema="across",
    )
    op.drop_table("user_service_account", schema="across")
