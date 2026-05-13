"""add permissions and roles data

Revision ID: 043885e1cd78
Revises: 80ed2c402962
Create Date: 2025-05-06 11:29:32.046897

"""

from typing import Sequence, TypedDict, Union
from uuid import UUID

from alembic import op
from sqlalchemy import orm, select

from migrations.util.build_role import build_role
from migrations.versions.model_snapshots import models_2025_05_06 as snapshot_models

# revision identifiers, used by Alembic.
revision: str = "043885e1cd78"
down_revision: Union[str, None] = "80ed2c402962"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class PermissionData(TypedDict):
    id: UUID
    name: str


class RoleData(TypedDict):
    id: UUID
    name: str
    permissions: list[str]


permission_data: dict[str, UUID] = {
    "all:write": UUID("399425fc-fcd4-4e3c-828b-2e65827d9293"),
    "system:schedule:write": UUID("5192dac3-7e0e-4063-b84e-01dc55f0ebaa"),
    "group:all:write": UUID("cc1042de-88ef-45b4-98f0-f14efb8734fb"),
    "group:read": UUID("0a0049b6-685c-4597-a174-ab9e1c046d40"),
    "group:write": UUID("f98b5355-7238-40b9-885a-a5a9272eb462"),
    "group:user:read": UUID("a9a4e49f-bcf7-475e-a7d5-19aea6e12c34"),
    "group:user:write": UUID("985bc7a1-0f67-4b19-8693-2477c2d484fc"),
    "group:role:write": UUID("35fb0ec8-68a5-4dc5-9375-8992ec001c38"),
    "group:observatory:write": UUID("da96a8f9-c245-49e9-801f-b2c5465d13f2"),
    "group:telescope:write": UUID("c437b47b-001a-428a-88b2-d9625a74de65"),
    "group:instrument:write": UUID("9f528e0e-9a8b-4a9d-a446-08aafc091d2a"),
    "group:schedule:write": UUID("c43cb665-1572-4b37-a225-4a03fa52c0a6"),
}

role_data: dict[str, RoleData] = {
    "system_role": {
        "id": UUID("ed6a2440-79c8-454a-8284-f826a27f6e04"),
        "name": "System Role",
        "permissions": ["system:schedule:write"],
    },
}


def upgrade() -> None:
    conn = op.get_bind()
    session = orm.Session(conn)

    permissions = {
        name: snapshot_models.Permission(id=id, name=name)
        for name, id in permission_data.items()
    }
    roles = [
        build_role(
            role, snapshot_models.Role, permission_data, snapshot_models.Permission
        )
        for role in role_data.values()
    ]

    # filter permissions to only those that are not associated with the roles we're adding, to avoid unique constraint violations
    filtered_permissions = {
        perm
        for name, perm in permissions.items()
        if not any(name in role["permissions"] for role in role_data.values())
    }

    session.add_all([*filtered_permissions, *roles])

    session.commit()


def downgrade() -> None:
    conn = op.get_bind()
    session = orm.Session(conn)

    # Delete permissions and roles by id
    perms = session.scalars(
        select(snapshot_models.Permission).where(
            snapshot_models.Permission.id.in_(permission_data.values())
        )
    ).all()

    for perm in perms:
        session.delete(perm)

    role = session.get(snapshot_models.Role, role_data["system_role"]["id"])
    session.delete(role)

    session.commit()
