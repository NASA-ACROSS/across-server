import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    MetaData,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from across_server.db.config import config

base_metadata = MetaData(schema=config.ACROSS_DB_NAME, quote_schema=True)


class CreatableMixin:
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    created_on: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class ModifiableMixin:
    modified_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    modified_on: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class Base(AsyncAttrs, DeclarativeBase):
    metadata = base_metadata
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class Observatory(Base):
    __tablename__ = "observatory"

    telescopes: Mapped[list["Telescope"]] = relationship(
        back_populates="observatory", lazy="noload"
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100))
    short_name: Mapped[str] = mapped_column(String(50), nullable=True)


class Telescope(Base):
    __tablename__ = "telescope"

    instruments: Mapped[list["Instrument"]] = relationship(
        back_populates="telescope", lazy="noload"
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    observatory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("observatory.id"), nullable=False, index=True
    )
    observatory: Mapped["Observatory"] = relationship(
        back_populates="telescopes", lazy="noload"
    )


class Instrument(Base):
    __tablename__ = "instrument"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    telescope_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("telescope.id"), nullable=False, index=True
    )
    settings: Mapped[list["InstrumentSetting"]] = relationship(
        back_populates="instrument", lazy="noload", cascade="all,delete"
    )
    telescope: Mapped["Telescope"] = relationship(
        back_populates="instruments", lazy="noload"
    )


class Setting(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "setting"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    instruments: Mapped[list["InstrumentSetting"]] = relationship(
        back_populates="setting", lazy="selectin", cascade="all,delete"
    )


class InstrumentSetting(Base, CreatableMixin, ModifiableMixin):
    __tablename__ = "instrument_setting"

    instrument_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("instrument.id"), primary_key=True
    )
    setting_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("setting.id"), primary_key=True
    )
    value: Mapped[str] = mapped_column(String(100), nullable=False)

    instrument: Mapped["Instrument"] = relationship(
        back_populates="settings", lazy="selectin"
    )
    setting: Mapped["Setting"] = relationship(
        back_populates="instruments", lazy="selectin"
    )
