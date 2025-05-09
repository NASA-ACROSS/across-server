"""add permissions and roles data

Revision ID: 043885e1cd78
Revises: 0f2036717762
Create Date: 2025-05-06 11:29:32.046897

"""

from typing import Sequence, Type, TypeVar, Union
from uuid import UUID

from alembic import op
from sqlalchemy import orm, select
from sqlalchemy.orm import DeclarativeBase

from migrations.versions.model_snapshots import models_2025_05_06 as snapshot_models

# revision identifiers, used by Alembic.
revision: str = "043885e1cd78"
down_revision: Union[str, None] = "0f2036717762"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

permission_data = {
    "all_write": {
        "id": UUID("399425fc-fcd4-4e3c-828b-2e65827d9293"),
        "name": "all:write",
    },
    "system_schedule_write": {
        "id": UUID("5192dac3-7e0e-4063-b84e-01dc55f0ebaa"),
        "name": "system:schedule:write",
    },
    "group_all_write": {
        "id": UUID("cc1042de-88ef-45b4-98f0-f14efb8734fb"),
        "name": "group:all:write",
    },
    "group_read": {
        "id": UUID("0a0049b6-685c-4597-a174-ab9e1c046d40"),
        "name": "group:read",
    },
    "group_write": {
        "id": UUID("f98b5355-7238-40b9-885a-a5a9272eb462"),
        "name": "group:write",
    },
    "group_user_read": {
        "id": UUID("a9a4e49f-bcf7-475e-a7d5-19aea6e12c34"),
        "name": "group:user:read",
    },
    "group_user_write": {
        "id": UUID("985bc7a1-0f67-4b19-8693-2477c2d484fc"),
        "name": "group:user:write",
    },
    "group_role_write": {
        "id": UUID("35fb0ec8-68a5-4dc5-9375-8992ec001c38"),
        "name": "group:role:write",
    },
    "observatory_write": {
        "id": UUID("da96a8f9-c245-49e9-801f-b2c5465d13f2"),
        "name": "group:observatory:write",
    },
    "telescope_write": {
        "id": UUID("c437b47b-001a-428a-88b2-d9625a74de65"),
        "name": "group:telescope:write",
    },
    "instrument_write": {
        "id": UUID("9f528e0e-9a8b-4a9d-a446-08aafc091d2a"),
        "name": "group:instrument:write",
    },
    "schedule_write": {
        "id": UUID("c43cb665-1572-4b37-a225-4a03fa52c0a6"),
        "name": "group:schedule:write",
    },
}

role_data = {
    "system_role": {
        "id": UUID("ed6a2440-79c8-454a-8284-f826a27f6e04"),
        "name": "System Role",
        "permissions": ["system_schedule_write"],
    },
}

T = TypeVar("T", bound="DeclarativeBase")


def build_role(data: dict, role_cls: Type[T], permission_cls: Type[T]):
    perms = [permission_cls(**permission_data[name]) for name in data["permissions"]]

    return role_cls(
        **{k: v for k, v in data.items() if k != "permissions"},
        permissions=perms,
    )


def upgrade() -> None:
    conn = op.get_bind()
    session = orm.Session(conn)

    permissions = {
        k: snapshot_models.Permission(**v) for k, v in permission_data.items()
    }
    roles = [
        snapshot_models.Role(
            **{k: v for k, v in role.items() if k != "permissions"},
            permissions=[permissions.get(name) for name in role["permissions"]],
        )
        for role in role_data.values()
    ]

    session.add_all([*permissions.values(), *roles])

    session.commit()


def downgrade() -> None:
    conn = op.get_bind()
    session = orm.Session(conn)

    # Delete permissions and roles by id
    perms = session.scalars(
        select(snapshot_models.Permission).where(
            snapshot_models.Permission.id.in_(
                permission["id"] for permission in permission_data.values()
            )
        )
    ).all()

    for perm in perms:
        session.delete(perm)

    role = session.get(snapshot_models.Role, role_data["system_role"]["id"])
    session.delete(role)

    session.commit()
