"""add tle scope to system role

Revision ID: 59faf999b470
Revises: d829f34da2f8
Create Date: 2025-09-18 14:54:15.847131

"""

from typing import Sequence, Union
from uuid import UUID

from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_09_02 as models

# revision identifiers, used by Alembic.
revision: str = "59faf999b470"
down_revision: Union[str, None] = "d829f34da2f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tle_permission_values = {
    "name": "system:tle:write",
    "id": UUID("f210ab41-7066-410f-ae08-c8916d4b1c0a"),
}


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    # system role by uuid from db
    system_role: models.Role = session.get(
        models.Role, UUID("ed6a2440-79c8-454a-8284-f826a27f6e04"), with_for_update=True
    )  # type: ignore
    # add permission
    system_role.permissions.append(models.Permission(**tle_permission_values))

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    tle_permission: models.Permission = session.get(
        models.Permission, tle_permission_values["id"]
    )  # type: ignore
    session.delete(tle_permission)

    session.commit()
