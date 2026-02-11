"""fix_central_wavelengths_for_filters

Revision ID: cc55dd06ba45
Revises: 9032acd18e5d
Create Date: 2026-02-06 10:47:46.804412

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm, update

import migrations.versions.model_snapshots.models_2025_11_17 as models
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
from migrations.versions.observatory_snapshots.keck.filters_2026_02_06 import (
    DEIMOS_FILTERS as NEW_DEIMOS_FILTERS,
)
from migrations.versions.observatory_snapshots.keck.filters_2026_02_06 import (
    LRIS_FILTERS as NEW_LRIS_FILTERS,
)
from migrations.versions.observatory_snapshots.keck.filters_2026_02_06 import (
    NIRC2_FILTERS as NEW_NIRC2_FILTERS,
)
from migrations.versions.observatory_snapshots.xmm_newton.filters_2026_02_06 import (
    OM_FILTERS as NEW_OM_FILTERS,
)

# Filters that need to be adjusted--both the newly calculated
# filter values and their old values for each affected instrument
INSTRUMENT_FILTERS: dict[str, list[dict]] = {
    "HST_ACS": NEW_ACS_WFC_FILTERS,
    "HST_WFC3_UVIS": NEW_WFC3_UVIS_FILTERS,
    "HST_WFC3_IR": NEW_WFC3_IR_FILTERS,
    "HST_COS": NEW_COS_FILTERS,
    "HST_STIS": NEW_STIS_FILTERS,
    "KECK_DEIMOS": NEW_DEIMOS_FILTERS,
    "KECK_LRIS": NEW_LRIS_FILTERS,
    "KECK_NIRC2": NEW_NIRC2_FILTERS,
    "XMM_NEWTON_OM": NEW_OM_FILTERS,
}

# revision identifiers, used by Alembic.
revision: str = "cc55dd06ba45"
down_revision: Union[str, None] = "9032acd18e5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    for instrument_name, instrument_filter_list in INSTRUMENT_FILTERS.items():
        for filter_data in instrument_filter_list:
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
    # Don't downgrade to old incorrect values, so do nothing
    pass
