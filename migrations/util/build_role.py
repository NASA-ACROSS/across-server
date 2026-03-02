from typing import Type, TypedDict, TypeVar
from uuid import UUID

from sqlalchemy import orm

# both are models but we return only the Role model
R = TypeVar("R", bound="orm.DeclarativeBase", covariant=True)
P = TypeVar("P", bound="orm.DeclarativeBase", covariant=True)


class RoleData(TypedDict):
    id: UUID
    name: str
    permissions: list[str]


def build_role(
    role: RoleData,
    role_cls: Type[R],
    perms: dict[str, UUID],
    permission_cls: Type[P],
) -> R:
    permissions = [
        permission_cls(id=perms[name], name=name)
        for name in role["permissions"]
        if name in perms
    ]

    return role_cls(
        **{k: v for k, v in role.items() if k != "permissions"},
        permissions=permissions,
    )
