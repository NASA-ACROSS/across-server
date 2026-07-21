"""adding observation request group permissions

Revision ID: 5a093993a1a3
Revises: 56f11c079a8b
Create Date: 2026-07-10 15:12:32.356187

"""

from typing import Sequence, Union
from uuid import UUID

from alembic import op
from sqlalchemy import orm, select

from migrations.versions.model_snapshots import models_2026_05_26 as snapshot_models

# revision identifiers, used by Alembic.
revision: str = "5a093993a1a3"
down_revision: Union[str, None] = "56f11c079a8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


permission_data: dict[str, UUID] = {
    "group:observation-request:write": UUID("f7bb4ed0-d2d1-4e81-bd98-cd782845844f"),
    "group:observation-request:read": UUID("106987c0-7845-437a-a7da-d79f2e985451"),
}


def upgrade() -> None:
    conn = op.get_bind()
    session = orm.Session(conn)

    permissions = [
        snapshot_models.Permission(id=id, name=name)
        for name, id in permission_data.items()
    ]

    session.add_all(permissions)
    session.commit()


def downgrade() -> None:
    conn = op.get_bind()
    session = orm.Session(conn)

    permissions = session.scalars(
        select(snapshot_models.Permission).where(
            snapshot_models.Permission.id.in_(permission_data.values())
        )
    ).all()

    for permission in permissions:
        session.delete(permission)

    session.commit()
