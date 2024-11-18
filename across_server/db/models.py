from __future__ import annotations

import uuid

from datetime import datetime
from typing import List, Optional, cast, get_args

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Enum,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
    relationship,
    declared_attr,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from geoalchemy2 import Geography, WKBElement

from ..routes.observatory.enums import OBSERVATORY_TYPE


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


## Mixins ##
class CreatableMixin:
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id"), nullable=True
    )
    created_on: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    @declared_attr
    def created_by(self) -> Mapped["User"]:
        return relationship(
            "User", foreign_keys=[cast(Mapped[uuid.UUID], self.created_by_id)]
        )


class ModifiableMixin:
    modified_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id"), nullable=True
    )
    modified_on: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, onupdate=func.now()
    )

    @declared_attr
    def modified_by(self) -> Mapped["User"]:
        return relationship(
            "User", foreign_keys=[cast(Mapped[uuid.UUID], self.modified_by_id)]
        )


## Associations/Join Tables ##
user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("group_id", ForeignKey("group.id"), primary_key=True),
)

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)

user_group_role = Table(
    "user_group_role",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("group_role_id", ForeignKey("group_role.id"), primary_key=True),
)

role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("permission_id", ForeignKey("permission.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)

group_role_permission = Table(
    "group_role_permission",
    Base.metadata,
    Column("permission_id", ForeignKey("permission.id"), primary_key=True),
    Column("group_role_id", ForeignKey("group_role.id"), primary_key=True),
)

group_observatory = Table(
    "group_observatory",
    Base.metadata,
    Column("group_id", ForeignKey("group.id"), primary_key=True),
    Column("observatory_id", ForeignKey("observatory.id"), primary_key=True),
)


## Application Models
class GroupInvite(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "group_invite"

    group_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("group.id"),
    )
    receiver_email: Mapped[str] = mapped_column(String(100))
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=True,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user.id"),
    )

    receiver: Mapped["User"] = relationship(
        back_populates="received_invites",
        foreign_keys=[receiver_id],
        lazy="selectin",
    )

    sender: Mapped["User"] = relationship(
        back_populates="sent_invites",
        foreign_keys=[sender_id],
        lazy="selectin",
    )

    group: Mapped["Group"] = relationship(
        back_populates="invites",
        foreign_keys=[group_id],
        lazy="selectin",
    )


class Permission(Base, CreatableMixin):
    __tablename__ = "permission"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permission, back_populates="permissions", lazy="selectin"
    )

    group_roles: Mapped[List["GroupRole"]] = relationship(
        secondary=group_role_permission, back_populates="permissions", lazy="selectin"
    )


class Role(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "role"

    name: Mapped[str] = mapped_column(String(100))

    users: Mapped[List["User"]] = relationship(
        secondary=user_role, back_populates="roles", lazy="selectin"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        secondary=role_permission, back_populates="roles", lazy="selectin"
    )


class GroupRole(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "group_role"

    name: Mapped[str] = mapped_column(String(100))
    group_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("group.id")
    )

    group: Mapped["Group"] = relationship(
        foreign_keys=[group_id], back_populates="roles"
    )
    users: Mapped[Optional[List["User"]]] = relationship(
        secondary=user_group_role, back_populates="group_roles", lazy="selectin"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        secondary=group_role_permission, back_populates="group_roles", lazy="selectin"
    )


class User(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(25), index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    groups: Mapped[Optional[List["Group"]]] = relationship(
        secondary=user_group, back_populates="users", lazy="selectin"
    )
    roles: Mapped[List["Role"]] = relationship(
        secondary=user_role, back_populates="users", lazy="selectin"
    )
    group_roles: Mapped[Optional[List["GroupRole"]]] = relationship(
        secondary=user_group_role, back_populates="users", lazy="selectin"
    )
    received_invites: Mapped[List["GroupInvite"]] = relationship(
        back_populates="receiver",
        lazy="selectin",
        foreign_keys=[GroupInvite.receiver_id],
    )
    sent_invites: Mapped[List["GroupInvite"]] = relationship(
        back_populates="sender",
        lazy="selectin",
        foreign_keys=[GroupInvite.sender_id],
    )


class Group(Base, CreatableMixin, ModifiableMixin):
    __tablename__: str = "group"

    name: Mapped[str] = mapped_column(String(256))
    short_name: Mapped[str] = mapped_column(String(25), index=True)

    users: Mapped[List["User"]] = relationship(
        secondary=user_group, back_populates="groups", lazy="selectin"
    )
    observatories: Mapped[List["Observatory"]] = relationship(
        secondary=group_observatory, back_populates="group", lazy="selectin"
    )
    roles: Mapped[Optional[List["GroupRole"]]] = relationship(
        back_populates="group",
        lazy="selectin",
        cascade="all,delete",
    )
    invites: Mapped[Optional[List["GroupInvite"]]] = relationship(
        back_populates="group", lazy="selectin"
    )


class Observatory(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "observatory"

    name: Mapped[str] = mapped_column(String(100))
    short_name: Mapped[str] = mapped_column(String(50), nullable=True)
    observatory_type: Mapped[OBSERVATORY_TYPE] = mapped_column(
        Enum(
            *get_args(OBSERVATORY_TYPE),
            name="observatory_type",
            create_constraint=True,
            validate_strings=True,
        )
    )

    telescopes: Mapped[List["Telescope"]] = relationship(
        back_populates="observatory", lazy="selectin", cascade="all,delete"
    )
    group: Mapped["Group"] = relationship(
        secondary=group_observatory,
        back_populates="observatories",
        lazy="selectin",
    )


class Telescope(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "telescope"

    name: Mapped[str] = mapped_column(String(100))
    short_name: Mapped[str] = mapped_column(String(50), nullable=True)
    observatory_id: Mapped[int] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Observatory.id)
    )

    observatory: Mapped["Observatory"] = relationship(
        back_populates="telescopes", lazy="selectin"
    )
    instruments: Mapped[List["Instrument"]] = relationship(
        back_populates="telescope", lazy="selectin", cascade="all,delete"
    )


class Instrument(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "instrument"

    name: Mapped[str] = mapped_column(String(100))
    short_name: Mapped[str] = mapped_column(String(50), nullable=True)
    telescope_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Telescope.id)
    )

    telescope: Mapped["Telescope"] = relationship(
        back_populates="instruments", lazy="selectin"
    )
    footprints: Mapped[List["Footprint"]] = relationship(
        back_populates="instrument", lazy="selectin", cascade="all,delete"
    )


class Footprint(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "footprint"

    instrument_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Instrument.id)
    )
    polygon: Mapped[WKBElement] = mapped_column(
        Geography("POLYGON", srid=4326), nullable=True
    )

    instrument: Mapped["Instrument"] = relationship(
        back_populates="footprints", lazy="selectin"
    )
