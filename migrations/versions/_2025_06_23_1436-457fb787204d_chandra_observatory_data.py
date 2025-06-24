"""Chandra observatory data

Revision ID: 457fb787204d
Revises: d4208fedfabf
Create Date: 2025-06-23 14:36:16.082498

"""

import uuid
from typing import Sequence, Union

from across.tools import EnergyBandpass, convert_to_wave
from across.tools.core import enums as tools_enums
from alembic import op
from sqlalchemy import orm

import migrations.versions.model_snapshots.models_2025_06_18 as snapshot_models
from across_server.core.enums import (
    EphemerisType,
    InstrumentFOV,
    InstrumentType,
    ObservatoryType,
)
from migrations.build_records import ssa_records
from migrations.db_util import arcmin_to_deg, circular_footprint

# revision identifiers, used by Alembic.
revision: str = "457fb787204d"
down_revision: Union[str, None] = "d4208fedfabf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# We've decided that, at least as a first pass, we'll treat the ACIS
# and HRC footprints as circles with radii of 8.5' and 15.5' respectively
acis_footprint = circular_footprint(radius_deg=arcmin_to_deg(8.5))
hrc_footprint = circular_footprint(radius_deg=arcmin_to_deg(15.5))

# Bandpass information found here: https://cxc.harvard.edu/cdo/about_chandra/
ACIS_BANDPASS = convert_to_wave(
    EnergyBandpass(min=0.1, max=10, unit=tools_enums.EnergyUnit.keV)
)

HRC_BANDPASS = convert_to_wave(
    EnergyBandpass(min=0.08, max=10, unit=tools_enums.EnergyUnit.keV)
)

HETG_BANDPASS = convert_to_wave(
    EnergyBandpass(min=0.4, max=10, unit=tools_enums.EnergyUnit.keV)
)

LETG_BANDPASS = convert_to_wave(
    EnergyBandpass(min=0.07, max=8.86, unit=tools_enums.EnergyUnit.keV)
)

# We are also treating each instrument + grating/mode combination
# as a unique Instrument data model, as the grating and observing mode
# affects the type, bandpass, and footprint of the observations
OBSERVATORY = {
    "id": uuid.UUID("6291c894-5e0c-4d80-a84c-e04b257f085d"),
    "name": "Chandra X-ray Observatory",
    "short_name": "Chandra",
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://chandra.harvard.edu/index.html",
    "telescopes": [
        {
            "id": uuid.UUID("310a569b-3280-48e7-9a53-1e2f2a88565f"),
            "name": "Chandra X-ray Telescope",
            "short_name": "Chandra",
            "reference_url": "https://cxc.harvard.edu/cdo/about_chandra/overview_cxo.html",
            "instruments": [
                {
                    "id": uuid.UUID("5020bf3f-6784-4e5c-99c2-2eb75f557c5a"),
                    "name": "Advanced CCD Imaging Spectrometer",
                    "short_name": "ACIS",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": acis_footprint,
                    "type": InstrumentType.CALORIMETER.value,
                    "reference_url": "https://cxc.harvard.edu/cal/Acis/index.html",
                    "filters": [
                        {
                            "name": "Chandra ACIS",
                            "id": uuid.UUID("c5a86d20-010f-46c4-bfb8-c9ad4477fedc"),
                            "min_wavelength": ACIS_BANDPASS.min,
                            "max_wavelength": ACIS_BANDPASS.max,
                            "reference_url": "https://cxc.harvard.edu/cdo/about_chandra/",
                        }
                    ],
                },
                {
                    "id": uuid.UUID("e570ae2a-16a5-4a75-b7f2-7905e4b4357c"),
                    "name": "Advanced CCD Imaging Spectrometer - High Energy Transmission Grating",
                    "short_name": "ACIS-HETG",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": [],
                    "type": InstrumentType.XRAY_COUNTING_SPECTROMETER.value,
                    "reference_url": "https://cxc.harvard.edu/cal/Acis/index.html",
                    "filters": [
                        {
                            "name": "Chandra HETG",
                            "id": uuid.UUID("f4a9f105-881b-4755-892a-affc4263a870"),
                            "min_wavelength": HETG_BANDPASS.min,
                            "max_wavelength": HETG_BANDPASS.max,
                            "reference_url": "https://cxc.harvard.edu/cdo/about_chandra/",
                        },
                    ],
                },
                {
                    "id": uuid.UUID("bcb48363-0d18-456f-a30e-31ac29b9031e"),
                    "name": "Advanced CCD Imaging Spectrometer - Low Energy Transmission Grating",
                    "short_name": "ACIS-LETG",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": [],
                    "type": InstrumentType.XRAY_COUNTING_SPECTROMETER.value,
                    "reference_url": "https://cxc.harvard.edu/cal/Acis/index.html",
                    "filters": [
                        {
                            "name": "Chandra LETG",
                            "id": uuid.UUID("d2253a04-f3aa-486c-a98b-84dfb3d14c47"),
                            "min_wavelength": LETG_BANDPASS.min,
                            "max_wavelength": LETG_BANDPASS.max,
                            "reference_url": "https://cxc.harvard.edu/cdo/about_chandra/",
                        },
                    ],
                },
                {
                    "id": uuid.UUID("71640140-237c-4a37-be89-28df12d19de7"),
                    "name": "Advanced CCD Imaging Spectrometer - Continuous Clocking Mode",
                    "short_name": "ACIS-CC",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": [],  # CC Mode sacrifices one spatial dimension for rapid CCD readout
                    "type": InstrumentType.CALORIMETER.value,
                    "reference_url": "https://cxc.harvard.edu/proposer/POG/html/chap6.html",
                    "filters": [
                        {
                            "name": "Chandra ACIS",
                            "id": uuid.UUID("9bd3e1b3-6ce6-40b3-b39a-b101e053de33"),
                            "min_wavelength": ACIS_BANDPASS.min,
                            "max_wavelength": ACIS_BANDPASS.max,
                            "reference_url": "https://cxc.harvard.edu/cdo/about_chandra/",
                        }
                    ],
                },
                {
                    "id": uuid.UUID("154c47c6-9bbb-41e2-9b1f-668db8c3443a"),
                    "name": "High Resolution Camera",
                    "short_name": "HRC",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": hrc_footprint,
                    "type": InstrumentType.CALORIMETER.value,
                    "reference_url": "https://cxc.harvard.edu/cal/Hrc/index.html",
                    "filters": [
                        {
                            "name": "Chandra HRC",
                            "id": uuid.UUID("2730a14d-af6e-4c3a-a5f3-37faa46e0952"),
                            "min_wavelength": HRC_BANDPASS.min,
                            "max_wavelength": HRC_BANDPASS.max,
                            "reference_url": "https://cxc.harvard.edu/cdo/about_chandra/",
                        }
                    ],
                },
                {
                    "id": uuid.UUID("addb76ca-002d-4af1-97a3-e1f6f58680cb"),
                    "name": "High Resolution Camera - High Energy Transmission Grating",
                    "short_name": "HRC-HETG",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": [],
                    "type": InstrumentType.XRAY_COUNTING_SPECTROMETER.value,
                    "reference_url": "https://cxc.harvard.edu/cal/Hrc/index.html",
                    "filters": [
                        {
                            "name": "Chandra HETG",
                            "id": uuid.UUID("a2a6f99c-af5b-4276-a260-3972667ca9c1"),
                            "min_wavelength": HETG_BANDPASS.min,
                            "max_wavelength": HETG_BANDPASS.max,
                            "reference_url": "https://cxc.harvard.edu/cdo/about_chandra/",
                        },
                    ],
                },
                {
                    "id": uuid.UUID("1e760bca-cca6-4342-a513-6d922dd2dbf0"),
                    "name": "High Resolution Camera - Low Energy Transmission Grating",
                    "short_name": "HRC-LETG",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": [],
                    "type": InstrumentType.XRAY_COUNTING_SPECTROMETER.value,
                    "reference_url": "https://cxc.harvard.edu/cal/Hrc/index.html",
                    "filters": [
                        {
                            "name": "Chandra LETG",
                            "id": uuid.UUID("8ff252a8-c858-4987-9649-cfa00bb35bbb"),
                            "min_wavelength": LETG_BANDPASS.min,
                            "max_wavelength": LETG_BANDPASS.max,
                            "reference_url": "https://cxc.harvard.edu/cdo/about_chandra/",
                        },
                    ],
                },
                {
                    "id": uuid.UUID("ea324f6f-20ea-4945-8dd6-9dbc44704e8a"),
                    "name": "High Resolution Camera - Timing Mode",
                    "short_name": "HRC-Timing",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": hrc_footprint,
                    "type": InstrumentType.CALORIMETER.value,
                    "reference_url": "https://cxc.harvard.edu/cal/Hrc/index.html",
                    "filters": [
                        {
                            "name": "Chandra HRC",
                            "id": uuid.UUID("86c51047-57ef-4807-b76e-32a3e646d6f3"),
                            "min_wavelength": HRC_BANDPASS.min,
                            "max_wavelength": HRC_BANDPASS.max,
                            "reference_url": "https://cxc.harvard.edu/cdo/about_chandra/",
                        },
                    ],
                },
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("c0a0c9bb-453a-452e-87ac-0b357864f02f"),
            "ephemeris_type": EphemerisType.TLE.value,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("5be955dc-8669-4fea-9bf5-cf6f51afd58a"),
                "norad_id": 25867,
                "norad_satellite_name": "CXO",
            },
        }
    ],
    "group": {
        "id": uuid.UUID("672f1553-81b0-423c-a17e-369139036c57"),
        "name": "Chandra X-ray Observatory",
        "short_name": "Chandra",
        "group_admin": {
            "id": uuid.UUID("56291c83-7c82-4515-a5d1-1dec60f7bae4"),
            "name": "Chandra Group Admin",
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
