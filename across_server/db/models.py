import uuid
from datetime import datetime, timezone

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import (
    JSON,
    REAL,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from ..core.enums.visibility_type import VisibilityType
from .config import config

base_metadata = MetaData(schema=config.ACROSS_DB_NAME, quote_schema=True)


class Base(AsyncAttrs, DeclarativeBase):
    metadata = base_metadata
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


## Mixins ##
class CreatableMixin:
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    created_on: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class ModifiableMixin:
    modified_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    modified_on: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
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

user_service_account = Table(
    "user_service_account",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("service_account_id", ForeignKey("service_account.id"), primary_key=True),
    # service_account_id can only appear once since SA can only be linked once PER user.
    UniqueConstraint("service_account_id", name="uq_service_account_id"),
)

service_account_role = Table(
    "service_account_role",
    Base.metadata,
    Column("service_account_id", ForeignKey("service_account.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)

service_account_group_role = Table(
    "service_account_group_role",
    Base.metadata,
    Column("service_account_id", ForeignKey("service_account.id"), primary_key=True),
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


instrument_constraint = Table(
    "instrument_constraint",
    Base.metadata,
    Column("instrument_id", ForeignKey("instrument.id"), primary_key=True),
    Column("constraint_id", ForeignKey("constraint.id"), primary_key=True),
)


class EarthLocationParameters(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "earth_location_parameters"

    observatory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True
    )
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)


class TLEParameters(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "tle_parameters"

    observatory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True
    )
    norad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    norad_satellite_name: Mapped[str] = mapped_column(String(69), nullable=False)
    __table_args__ = (
        UniqueConstraint(
            "norad_id", "observatory_id", name="uq_norad_id_observatory_id"
        ),  # Enforce uniqueness
    )


class JPLEphemerisParameters(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "jpl_ephemeris_parameters"

    observatory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True
    )
    naif_id: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint(
            "naif_id", "observatory_id", name="uq_naif_id_observatory_id"
        ),  # Enforce uniqueness
    )


class SpiceKernelParameters(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "spice_kernel_parameters"

    observatory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True
    )
    naif_id: Mapped[int] = mapped_column(Integer, nullable=False)
    spice_kernel_url: Mapped[str] = mapped_column(String(256), nullable=False)


class ObservatoryEphemerisType(Base):
    __tablename__ = "observatory_ephemeris_type"
    __allow_unmapped__ = True

    observatory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("observatory.id"), primary_key=True
    )
    ephemeris_type: Mapped[str] = mapped_column(
        String(10), nullable=False, primary_key=True
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False)

    parameters: Base | None = None

    # Relationship to Observatory
    observatory: Mapped["Observatory"] = relationship(
        "Observatory", back_populates="ephemeris_types"
    )

    __table_args__ = (
        UniqueConstraint(
            "observatory_id",
            "ephemeris_type",
            "priority",
            name="uq_observatory_type_priority",
        ),
    )


# Application Models
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

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permission, back_populates="permissions", lazy="selectin"
    )

    group_roles: Mapped[list["GroupRole"]] = relationship(
        secondary=group_role_permission, back_populates="permissions", lazy="selectin"
    )


class Role(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "role"

    name: Mapped[str] = mapped_column(String(100))

    users: Mapped[list["User"]] = relationship(
        secondary=user_role, back_populates="roles", lazy="selectin"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permission, back_populates="roles", lazy="selectin"
    )
    service_accounts: Mapped[list["ServiceAccount"] | None] = relationship(
        secondary=service_account_role,
        back_populates="roles",
        lazy="selectin",
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
    users: Mapped[list["User"] | None] = relationship(
        secondary=user_group_role, back_populates="group_roles", lazy="selectin"
    )
    service_accounts: Mapped[list["ServiceAccount"] | None] = relationship(
        secondary=service_account_group_role,
        back_populates="group_roles",
        lazy="selectin",
    )
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=group_role_permission, back_populates="group_roles", lazy="selectin"
    )


class ServiceAccount(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "service_account"

    expiration: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expiration_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    hashed_key: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped[list["User"]] = relationship(
        secondary=user_service_account,
        back_populates="service_accounts",
        lazy="selectin",
    )
    roles: Mapped[list["Role"] | None] = relationship(
        secondary=service_account_role,
        back_populates="service_accounts",
        lazy="selectin",
    )
    group_roles: Mapped[list["GroupRole"]] = relationship(
        secondary=service_account_group_role,
        back_populates="service_accounts",
        lazy="selectin",
    )


class User(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(25), index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    groups: Mapped[list["Group"]] = relationship(
        secondary=user_group, back_populates="users", lazy="selectin"
    )
    roles: Mapped[list["Role"]] = relationship(
        secondary=user_role, back_populates="users", lazy="selectin"
    )
    group_roles: Mapped[list["GroupRole"]] = relationship(
        secondary=user_group_role, back_populates="users", lazy="selectin"
    )
    received_invites: Mapped[list["GroupInvite"]] = relationship(
        back_populates="receiver",
        lazy="selectin",
        foreign_keys=[GroupInvite.receiver_id],
    )
    sent_invites: Mapped[list["GroupInvite"]] = relationship(
        back_populates="sender",
        lazy="selectin",
        foreign_keys=[GroupInvite.sender_id],
    )
    service_accounts: Mapped[list["ServiceAccount"]] = relationship(
        secondary=user_service_account,
        back_populates="user",
        lazy="selectin",
    )


class Group(Base, CreatableMixin, ModifiableMixin):
    __tablename__: str = "group"

    name: Mapped[str] = mapped_column(String(256))
    short_name: Mapped[str] = mapped_column(String(25), index=True)

    users: Mapped[list["User"]] = relationship(
        secondary=user_group, back_populates="groups", lazy="selectin"
    )
    observatories: Mapped[list["Observatory"]] = relationship(
        secondary=group_observatory, back_populates="group", lazy="selectin"
    )
    roles: Mapped[list["GroupRole"]] = relationship(
        back_populates="group",
        lazy="selectin",
        cascade="all,delete",
    )
    invites: Mapped[list["GroupInvite"]] = relationship(
        back_populates="group", lazy="selectin"
    )


class Observatory(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "observatory"

    name: Mapped[str] = mapped_column(String(100))
    short_name: Mapped[str] = mapped_column(String(50), nullable=True)
    type: Mapped[str] = mapped_column(String(25), nullable=False)
    reference_url: Mapped[str] = mapped_column(String, nullable=True)
    is_operational: Mapped[bool] = mapped_column(Boolean, default=True)

    telescopes: Mapped[list["Telescope"]] = relationship(
        back_populates="observatory", lazy="selectin", cascade="all,delete"
    )
    group: Mapped["Group"] = relationship(
        secondary=group_observatory,
        back_populates="observatories",
        lazy="selectin",
    )
    ephemeris_types: Mapped[list["ObservatoryEphemerisType"]] = relationship(
        "ObservatoryEphemerisType", back_populates="observatory", cascade="all,delete"
    )
    operational_begin_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    operational_end_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )


class Telescope(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "telescope"

    name: Mapped[str] = mapped_column(String(100))
    short_name: Mapped[str] = mapped_column(String(50), nullable=True)
    observatory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Observatory.id)
    )
    reference_url: Mapped[str] = mapped_column(String, nullable=True)
    is_operational: Mapped[bool] = mapped_column(Boolean, default=True)

    observatory: Mapped["Observatory"] = relationship(
        back_populates="telescopes", lazy="selectin"
    )
    instruments: Mapped[list["Instrument"]] = relationship(
        back_populates="telescope", lazy="selectin", cascade="all,delete"
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="telescope", lazy="noload"
    )


class Instrument(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "instrument"

    name: Mapped[str] = mapped_column(String(100))
    short_name: Mapped[str] = mapped_column(String(50), nullable=True)
    telescope_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Telescope.id)
    )
    type: Mapped[str] = mapped_column(String(50))
    field_of_view: Mapped[str] = mapped_column(String(50))
    reference_url: Mapped[str] = mapped_column(String, nullable=True)
    is_operational: Mapped[bool] = mapped_column(Boolean, default=True)

    telescope: Mapped["Telescope"] = relationship(
        back_populates="instruments", lazy="selectin"
    )
    footprints: Mapped[list["Footprint"]] = relationship(
        back_populates="instrument", lazy="selectin", cascade="all,delete"
    )

    observations: Mapped[list["Observation"]] = relationship(
        back_populates="instrument", lazy="noload"
    )
    filters: Mapped[list["Filter"]] = relationship(
        back_populates="instrument", lazy="selectin", cascade="all,delete"
    )
    visibility_type: Mapped[VisibilityType] = mapped_column(String(10), nullable=True)
    constraints: Mapped[list["Constraint"]] = relationship(
        secondary=instrument_constraint,
        back_populates="instruments",
        lazy="selectin",
        cascade="all,delete",
    )


class Filter(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "filter"

    name: Mapped[str] = mapped_column(String(50))
    peak_wavelength: Mapped[float] = mapped_column(Float, nullable=True)
    min_wavelength: Mapped[float] = mapped_column(Float)
    max_wavelength: Mapped[float] = mapped_column(Float)
    is_operational: Mapped[bool] = mapped_column(Boolean, default=True)
    sensitivity_depth_unit: Mapped[str] = mapped_column(String(50), nullable=True)
    sensitivity_depth: Mapped[float] = mapped_column(Float, nullable=True)
    sensitivity_time_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    reference_url: Mapped[str] = mapped_column(String, nullable=True)
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Instrument.id)
    )

    instrument: Mapped["Instrument"] = relationship(
        back_populates="filters", lazy="selectin"
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


class Schedule(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "schedule"

    telescope_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Telescope.id)
    )
    date_range_begin: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_range_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(256), nullable=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    fidelity: Mapped[str] = mapped_column(String(50), default="high", nullable=False)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)

    telescope: Mapped["Telescope"] = relationship(
        back_populates="schedules", lazy="selectin"
    )

    observations: Mapped[list["Observation"]] = relationship(
        back_populates="schedule", lazy="selectin", cascade="all,delete"
    )

    __table_args__ = (
        Index("ix_schedule_date_range", "date_range_begin", "date_range_end"),
        Index("ix_schedule_date_range_begin", "date_range_begin"),
        Index("ix_schedule_date_range_end", "date_range_end"),
        Index("ix_schedule_checksum", "checksum"),
    )


class Observation(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "observation"

    instrument_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Instrument.id)
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Schedule.id)
    )
    object_name: Mapped[str] = mapped_column(String(100))
    pointing_ra: Mapped[float | None] = mapped_column(REAL())
    pointing_dec: Mapped[float | None] = mapped_column(REAL())
    pointing_position: Mapped[WKBElement | None] = mapped_column(
        Geography("POINT", srid=4326), nullable=True
    )
    date_range_begin: Mapped[datetime] = mapped_column(DateTime)
    date_range_end: Mapped[datetime] = mapped_column(DateTime)
    external_observation_id: Mapped[str] = mapped_column(String(50))
    type: Mapped[str] = mapped_column(String(50))  # Enum
    status: Mapped[str] = mapped_column(String(50))  # Enum
    exposure_time: Mapped[float | None] = mapped_column(REAL())
    reason: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(100))
    proposal_reference: Mapped[str | None] = mapped_column(String(100))
    object_ra: Mapped[float | None] = mapped_column(REAL())
    object_dec: Mapped[float | None] = mapped_column(REAL())
    object_position: Mapped[WKBElement | None] = mapped_column(
        Geography("POINT", srid=4326), nullable=True
    )
    pointing_angle: Mapped[float | None] = mapped_column(Float)
    depth_value: Mapped[float | None] = mapped_column(REAL())
    depth_unit: Mapped[str | None] = mapped_column(String(50))  # Enum
    max_wavelength: Mapped[float | None] = mapped_column(Float)
    min_wavelength: Mapped[float | None] = mapped_column(Float)
    peak_wavelength: Mapped[float | None] = mapped_column(Float)
    filter_name: Mapped[str | None] = mapped_column(String(50))

    # explicit ivoa ObsLocTap definitions
    t_resolution: Mapped[float | None] = mapped_column(Float, nullable=True)
    em_res_power: Mapped[float | None] = mapped_column(Float, nullable=True)
    o_ucd: Mapped[str | None] = mapped_column(String, nullable=True)
    pol_states: Mapped[str | None] = mapped_column(String, nullable=True)
    pol_xel: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Enum
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tracking_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Enum

    instrument: Mapped["Instrument"] = relationship(
        back_populates="observations", lazy="selectin"
    )
    schedule: Mapped["Schedule"] = relationship(
        back_populates="observations", lazy="selectin"
    )


class TLE(Base):
    __tablename__ = "tle"

    norad_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    epoch: Mapped[datetime] = mapped_column(DateTime, nullable=False, primary_key=True)
    satellite_name: Mapped[str] = mapped_column(String(69), nullable=False)
    tle1: Mapped[str] = mapped_column(String(69), nullable=False)
    tle2: Mapped[str] = mapped_column(String(69), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "epoch", "norad_id", name="uq_epoch_norad_id"
        ),  # Enforce uniqueness
    )


class Constraint(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "constraint"

    constraint_type: Mapped[str] = mapped_column(String(50), nullable=False)
    constraint_parameters: Mapped[dict] = mapped_column(JSON, nullable=False)

    instruments: Mapped[list["Instrument"]] = relationship(
        secondary=instrument_constraint,
        back_populates="constraints",
        lazy="selectin",
    )
