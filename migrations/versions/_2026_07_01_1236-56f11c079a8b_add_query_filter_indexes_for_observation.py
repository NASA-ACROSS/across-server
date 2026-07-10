"""add query filter indexes for observation

Revision ID: 56f11c079a8b
Revises: b230cfe44da5
Create Date: 2026-07-01 12:36:19.712195

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "56f11c079a8b"
down_revision: Union[str, None] = "b230cfe44da5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Covering index: instrument_id is a broad filter.
    # Include: status and type on index leaves to accelerate common compound filters
    op.create_index(
        "ix_across_observation_instrument_created_id",
        "observation",
        ["instrument_id", sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
        postgresql_include=["status", "type"],
    )

    # Covering index: status is a broad filter.
    # Include: type and instrument_id on index leaves to accelerate common compound filters
    op.create_index(
        "ix_across_observation_status_created_id",
        "observation",
        ["status", sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
        postgresql_include=["type", "instrument_id"],
    )

    # Plain composite indexes for remaining filter columns.
    op.create_index(
        "ix_across_observation_type_created_id",
        "observation",
        ["type", sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
    )
    op.create_index(
        "ix_across_observation_date_range_end_created_id",
        "observation",
        ["date_range_end", sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
    )
    op.create_index(
        "ix_across_observation_date_range_begin_created_id",
        "observation",
        ["date_range_begin", sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
    )
    op.create_index(
        "ix_across_observation_min_wavelength_created_id",
        "observation",
        ["min_wavelength", sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
    )
    op.create_index(
        "ix_across_observation_max_wavelength_created_id",
        "observation",
        ["max_wavelength", sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
    )
    op.create_index(
        "ix_across_observation_depth_value_created_id",
        "observation",
        ["depth_value", sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
    )
    op.create_index(
        "ix_across_observation_depth_unit_created_id",
        "observation",
        ["depth_unit", sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
    )

    # Default sort composite — created_on + id for no-filter pagination
    op.create_index(
        "ix_across_observation_created_on_id",
        "observation",
        [sa.text("created_on DESC"), sa.text("id DESC")],
        schema="across",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_across_observation_created_on_id",
        table_name="observation",
        schema="across",
    )
    op.drop_index(
        "ix_across_observation_depth_unit_created_id",
        table_name="observation",
        schema="across",
    )
    op.drop_index(
        "ix_across_observation_depth_value_created_id",
        table_name="observation",
        schema="across",
    )
    op.drop_index(
        "ix_across_observation_max_wavelength_created_id",
        table_name="observation",
        schema="across",
    )
    op.drop_index(
        "ix_across_observation_min_wavelength_created_id",
        table_name="observation",
        schema="across",
    )
    op.drop_index(
        "ix_across_observation_date_range_begin_created_id",
        table_name="observation",
        schema="across",
    )
    op.drop_index(
        "ix_across_observation_date_range_end_created_id",
        table_name="observation",
        schema="across",
    )
    op.drop_index(
        "ix_across_observation_type_created_id",
        table_name="observation",
        schema="across",
    )
    op.drop_index(
        "ix_across_observation_status_created_id",
        table_name="observation",
        schema="across",
    )
    op.drop_index(
        "ix_across_observation_instrument_created_id",
        table_name="observation",
        schema="across",
    )
