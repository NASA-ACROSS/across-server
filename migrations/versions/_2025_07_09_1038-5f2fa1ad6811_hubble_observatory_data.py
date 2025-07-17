"""Hubble observatory data

Revision ID: 5f2fa1ad6811
Revises: d41e0c380a1f
Create Date: 2025-07-09 10:38:04.554398

"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_06_18 as snapshot_models
from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from across_server.core.enums.observatory_type import ObservatoryType
from migrations.build_records import ssa_records
from migrations.db_util import arcsec_to_deg, parallelogram_footprint
from migrations.versions.observatory_snapshots.hubble.hubble_filters_2025_07_09 import (
    ACS_WFC_FILTERS,
    COS_FILTERS,
    STIS_FILTERS,
    WFC3_IR_FILTERS,
    WFC3_UVIS_FILTERS,
)

# revision identifiers, used by Alembic.
revision: str = "5f2fa1ad6811"
down_revision: Union[str, None] = "d41e0c380a1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Rotation angles for HST footprints can be found here:
# https://www.stsci.edu/hst/instrumentation/focus-and-pointing/fov-geometry

# Reference: https://hst-docs.stsci.edu/acsihb/chapter-3-acs-capabilities-design-and-operations/3-3-instrument-design
ACS_WFC_FOOTPRINT = parallelogram_footprint(
    arcsec_to_deg(202.0),
    arcsec_to_deg(202.0),
    92.163,
    177.552,
)

# Reference: https://hst-docs.stsci.edu/wfc3ihb/chapter-1-introduction-to-wfc3/1-3-key-features-of-wfc3
WFC3_UVIS_FOOTPRINT = parallelogram_footprint(
    arcsec_to_deg(162.0),
    arcsec_to_deg(162.0),
    -41.387,
    44.8315,
)

WFC3_IR_FOOTPRINT = parallelogram_footprint(
    arcsec_to_deg(136.0),
    arcsec_to_deg(123.0),
    -45.1232,
    44.5888,
)

# The STIS footprint technically depends on the detector,
# but 52 x 52 arcsec is the biggest (others are ~half the size)
# Reference: https://hst-docs.stsci.edu/stisihb/chapter-3-stis-capabilities-design-operations-and-observations/3-2-instrument-design
STIS_FOOTPRINT = parallelogram_footprint(
    arcsec_to_deg(52.0),
    arcsec_to_deg(52.0),
    45.0,
    135.0,
)


OBSERVATORY: dict = {
    "id": uuid.UUID("eb43bec9-0002-4c05-b294-de71453d95b6"),
    "name": "Hubble Space Telescope",
    "short_name": "HST",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://science.nasa.gov/mission/hubble/",
    "telescopes": [
        {
            "id": uuid.UUID("d8af2063-1a11-4941-aa06-2d63a9d9b918"),
            "name": "Hubble Space Telescope",
            "short_name": "HST",
            "is_operational": True,
            "reference_url": "https://science.nasa.gov/mission/hubble/",
            "instruments": [
                {
                    "id": uuid.UUID("34e16e2a-c355-4c5d-be90-cc207e62047c"),
                    "name": "Advanced Camera for Surveys",
                    "short_name": "HST_ACS",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": ACS_WFC_FOOTPRINT,
                    "reference_url": "https://science.nasa.gov/mission/hubble/observatory/design/advanced-camera-for-surveys/",
                    "filters": ACS_WFC_FILTERS,
                },
                {
                    "id": uuid.UUID("fd4b0ad5-7893-4696-8143-c2160fc6b228"),
                    "name": "Wide Field Camera 3 - Ultraviolet and Visual Channel",
                    "short_name": "HST_WFC3_UVIS",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": WFC3_UVIS_FOOTPRINT,
                    "reference_url": "https://science.nasa.gov/mission/hubble/observatory/design/wide-field-camera-3/",
                    "filters": WFC3_UVIS_FILTERS,
                },
                {
                    "id": uuid.UUID("09966d5c-8554-4256-8b88-71a899f2b9c5"),
                    "name": "Wide Field Camera 3 - Infrared Channel",
                    "short_name": "HST_WFC3_IR",
                    "type": InstrumentType.PHOTOMETRIC.value,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": WFC3_IR_FOOTPRINT,
                    "reference_url": "https://science.nasa.gov/mission/hubble/observatory/design/wide-field-camera-3/",
                    "filters": WFC3_IR_FILTERS,
                },
                {
                    "id": uuid.UUID("40dff0eb-535d-4df6-9cf2-ba5d1c665a73"),
                    "name": "Cosmic Origins Spectrograph",
                    "short_name": "HST_COS",
                    "type": InstrumentType.SPECTROSCOPIC_HIGH_RES.value,
                    "field_of_view": InstrumentFOV.POINT.value,
                    "footprint": [],
                    "reference_url": "https://science.nasa.gov/mission/hubble/observatory/design/cosmic-origins-spectrograph/",
                    "filters": COS_FILTERS,
                },
                {
                    "id": uuid.UUID("6f8a093c-33fe-4b82-b757-880ff90f34d4"),
                    "name": "Space Telescope Imaging Spectrograph",
                    "short_name": "HST_STIS",
                    "type": InstrumentType.PHOTOMETRIC.value,  # NOTE: STIS is an imager as well as a high and low-res spectrograph
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": STIS_FOOTPRINT,
                    "reference_url": "https://science.nasa.gov/mission/hubble/observatory/design/space-telescope-imaging-spectrograph/",
                    "filters": STIS_FILTERS,
                },
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("1d2007b5-228a-4eea-b245-4ccf7f657b19"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("0d17c6c2-e023-4c6b-b5f5-9abd13a1d280"),
                "norad_id": 20580,
                "norad_satellite_name": "HST",
            },
        },
    ],
    "group": {
        "id": uuid.UUID("f95900a2-13b4-4e3b-b1c5-832909914462"),
        "name": "Hubble Space Telescope",
        "short_name": "HST",
        "group_admin": {
            "id": uuid.UUID("63aba50c-d6b9-4123-88cb-fd8426e6f156"),
            "name": "HST Group Admin",
        },
    },
}


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    records = ssa_records.build(session, OBSERVATORY, snapshot_models)

    session.add_all(records)
    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    ssa_records.delete(session, OBSERVATORY, snapshot_models)

    session.commit()
