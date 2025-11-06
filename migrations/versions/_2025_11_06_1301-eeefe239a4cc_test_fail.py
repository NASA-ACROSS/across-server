"""test-fail

Revision ID: eeefe239a4cc
Revises: d56250541a9b
Create Date: 2025-11-06 13:01:44.121624

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm, select

from across_server.db import models

# revision identifiers, used by Alembic.
revision: str = "eeefe239a4cc"
down_revision: Union[str, None] = "d56250541a9b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    session.scalars(select(models.Role).filter_by(unknown="ERROR"))


def downgrade() -> None:
    pass
