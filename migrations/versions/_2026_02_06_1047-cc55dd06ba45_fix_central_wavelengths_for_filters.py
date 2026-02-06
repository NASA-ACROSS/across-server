"""fix_central_wavelengths_for_filters

Revision ID: cc55dd06ba45
Revises: 9032acd18e5d
Create Date: 2026-02-06 10:47:46.804412

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm, update

import migrations.versions.model_snapshots.models_2025_11_17 as models
from migrations.versions.observatory_snapshots.hubble.filters_2025_07_09 import (
    ACS_WFC_FILTERS as OLD_ACS_WFC_FILTERS,
)
from migrations.versions.observatory_snapshots.hubble.filters_2025_07_09 import (
    COS_FILTERS as OLD_COS_FILTERS,
)
from migrations.versions.observatory_snapshots.hubble.filters_2025_07_09 import (
    STIS_FILTERS as OLD_STIS_FILTERS,
)
from migrations.versions.observatory_snapshots.hubble.filters_2025_07_09 import (
    WFC3_IR_FILTERS as OLD_WFC3_IR_FILTERS,
)
from migrations.versions.observatory_snapshots.hubble.filters_2025_07_09 import (
    WFC3_UVIS_FILTERS as OLD_WFC3_UVIS_FILTERS,
)
from migrations.versions.observatory_snapshots.hubble.filters_2026_02_06 import (
    ACS_WFC_FILTERS as NEW_ACS_WFC_FILTERS,
)
from migrations.versions.observatory_snapshots.hubble.filters_2026_02_06 import (
    COS_FILTERS as NEW_COS_FILTERS,
)
from migrations.versions.observatory_snapshots.hubble.filters_2026_02_06 import (
    STIS_FILTERS as NEW_STIS_FILTERS,
)
from migrations.versions.observatory_snapshots.hubble.filters_2026_02_06 import (
    WFC3_IR_FILTERS as NEW_WFC3_IR_FILTERS,
)
from migrations.versions.observatory_snapshots.hubble.filters_2026_02_06 import (
    WFC3_UVIS_FILTERS as NEW_WFC3_UVIS_FILTERS,
)
from migrations.versions.observatory_snapshots.keck.filters_2025_10_08 import (
    DEIMOS_FILTERS as OLD_DEIMOS_FILTERS,
)
from migrations.versions.observatory_snapshots.keck.filters_2025_10_08 import (
    LRIS_FILTERS as OLD_LRIS_FILTERS,
)
from migrations.versions.observatory_snapshots.keck.filters_2025_10_08 import (
    NIRC2_FILTERS as OLD_NIRC2_FILTERS,
)
from migrations.versions.observatory_snapshots.keck.filters_2026_02_06 import (
    DEIMOS_FILTERS as NEW_DEIMOS_FILTERS,
)
from migrations.versions.observatory_snapshots.keck.filters_2026_02_06 import (
    LRIS_FILTERS as NEW_LRIS_FILTERS,
)
from migrations.versions.observatory_snapshots.keck.filters_2026_02_06 import (
    NIRC2_FILTERS as NEW_NIRC2_FILTERS,
)
from migrations.versions.observatory_snapshots.xmm_newton.filters_2025_08_12 import (
    OM_FILTERS as OLD_OM_FILTERS,
)
from migrations.versions.observatory_snapshots.xmm_newton.filters_2026_02_06 import (
    OM_FILTERS as NEW_OM_FILTERS,
)

# Filters that need to be adjusted--both the newly calculated
# filter values and their old values for each affected instrument
INSTRUMENT_FILTERS: dict[str, dict[str, list[dict]]] = {
    "HST_ACS": {
        "new_filters": NEW_ACS_WFC_FILTERS,
        "old_filters": OLD_ACS_WFC_FILTERS,
    },
    "HST_WFC3_UVIS": {
        "new_filters": NEW_WFC3_UVIS_FILTERS,
        "old_filters": OLD_WFC3_UVIS_FILTERS,
    },
    "HST_WFC3_IR": {
        "new_filters": NEW_WFC3_IR_FILTERS,
        "old_filters": OLD_WFC3_IR_FILTERS,
    },
    "HST_COS": {
        "new_filters": NEW_COS_FILTERS,
        "old_filters": OLD_COS_FILTERS,
    },
    "HST_STIS": {
        "new_filters": NEW_STIS_FILTERS,
        "old_filters": OLD_STIS_FILTERS,
    },
    "KECK_DEIMOS": {
        "new_filters": NEW_DEIMOS_FILTERS,
        "old_filters": OLD_DEIMOS_FILTERS,
    },
    "KECK_LRIS": {
        "new_filters": NEW_LRIS_FILTERS,
        "old_filters": OLD_LRIS_FILTERS,
    },
    "KECK_NIRC2": {
        "new_filters": NEW_NIRC2_FILTERS,
        "old_filters": OLD_NIRC2_FILTERS,
    },
    "XMM_NEWTON_OM": {
        "new_filters": NEW_OM_FILTERS,
        "old_filters": OLD_OM_FILTERS,
    },
}

# revision identifiers, used by Alembic.
revision: str = "cc55dd06ba45"
down_revision: Union[str, None] = "9032acd18e5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    for instrument_name, instrument_filter_dict in INSTRUMENT_FILTERS.items():
        for filter_data in instrument_filter_dict["new_filters"]:
            # Update filter data
            filter_id = filter_data.pop("id")
            session.execute(
                update(models.Filter)
                .where(models.Filter.id == filter_id)
                .values(**filter_data)
            )

            # Update observation data
            if instrument_name == "XMM_NEWTON_OM":
                # The filter name for XMM-Newton OM observations is different
                # than the name on the associated Filter model
                session.execute(
                    update(models.Observation)
                    .where(
                        models.Observation.filter_name
                        == filter_data["name"].replace("XMM-Newton ", "")
                    )
                    .values(
                        min_wavelength=filter_data["min_wavelength"],
                        max_wavelength=filter_data["max_wavelength"],
                    )
                )
            else:
                session.execute(
                    update(models.Observation)
                    .where(models.Observation.filter_name == filter_data["name"])
                    .values(
                        min_wavelength=filter_data["min_wavelength"],
                        max_wavelength=filter_data["max_wavelength"],
                    )
                )

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    for instrument_name, instrument_filter_dict in INSTRUMENT_FILTERS.items():
        for filter_data in instrument_filter_dict["old_filters"]:
            # Update filter data
            filter_id = filter_data.pop("id")
            session.execute(
                update(models.Filter)
                .where(models.Filter.id == filter_id)
                .values(**filter_data)
            )

            # Update observation data
            if instrument_name == "XMM_NEWTON_OM":
                # The filter name for XMM-Newton OM observations is different
                # than the name on the associated Filter model
                session.execute(
                    update(models.Observation)
                    .where(
                        models.Observation.filter_name
                        == filter_data["name"].replace("XMM-Newton ", "")
                    )
                    .values(
                        min_wavelength=filter_data["min_wavelength"],
                        max_wavelength=filter_data["max_wavelength"],
                    )
                )
            else:
                session.execute(
                    update(models.Observation)
                    .where(models.Observation.filter_name == filter_data["name"])
                    .values(
                        min_wavelength=filter_data["min_wavelength"],
                        max_wavelength=filter_data["max_wavelength"],
                    )
                )

    session.commit()
