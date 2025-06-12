"""add fermi

Revision ID: 7f001eadcb4a
Revises: a6590318e932
Create Date: 2025-05-19 15:15:20.099908

"""

import uuid
from typing import Sequence, Union

import numpy as np
from across.tools import EnergyBandpass, convert_to_wave
from across.tools.core import enums as tools_enums
from alembic import op
from sqlalchemy import orm

from across_server.core.enums import InstrumentType, ObservatoryType
from across_server.core.enums.ephemeris_type import EphemerisType
from across_server.core.enums.instrument_fov import InstrumentFOV
from migrations.build_records import ssa_records
from migrations.versions.model_snapshots import models_2025_05_15 as snapshot_models

# revision identifiers, used by Alembic.
revision: str = "7f001eadcb4a"
down_revision: Union[str, None] = "a6590318e932"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# LAT has a FOV of 2.4 steradians
radius = 50  # degrees
thetas = np.linspace(0, -2 * np.pi, 200)
ras = radius * np.cos(thetas)
decs = radius * np.sin(thetas)
LAT_FOOTPRINT = [[{"x": ras[i], "y": decs[i]} for i in range(len((ras)))]]

# Info about LAT and GBM bandpasses found here:
# https://heasarc.gsfc.nasa.gov/docs/heasarc/missions/fermi.html
LAT_ENERGY_BANDPASS = EnergyBandpass(
    min=0.02,
    max=300,
    unit=tools_enums.EnergyUnit.GeV,
)
LAT_WAVELENGTH_BANDPASS = convert_to_wave(LAT_ENERGY_BANDPASS)

GBM_ENERGY_BANDPASS = EnergyBandpass(
    min=0.008,
    max=40,
    unit=tools_enums.EnergyUnit.MeV,
)
GBM_WAVELENGTH_BANDPASS = convert_to_wave(GBM_ENERGY_BANDPASS)

OBSERVATORY = {
    "name": "Fermi Gamma-ray Space Telescope",
    "short_name": "Fermi",
    "id": uuid.UUID("3417942b-7cc9-4e91-a9ab-fbc800871ef5"),
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://fermi.gsfc.nasa.gov",
    "is_operational": True,
    "telescopes": [
        {
            "name": "Large Area Telescope",
            "short_name": "LAT",
            "id": uuid.UUID("222d5f4a-8fd6-4299-a696-b3a6cb13d7bc"),
            "is_operational": True,
            "reference_url": "https://fermi.gsfc.nasa.gov",
            "instruments": [
                {
                    "name": "Large Area Telescope",
                    "short_name": "LAT",
                    "id": uuid.UUID("7f7b97ed-e341-476f-908b-7bad8740b31b"),
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": LAT_FOOTPRINT,
                    "is_operational": True,
                    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/heasarc/missions/fermi.html",
                    "type": InstrumentType.CALORIMETER.value,
                    "filters": [
                        {
                            "name": "Fermi LAT Bandpass",
                            "id": uuid.UUID("415f0c75-111e-4970-b89d-b55cc5975a81"),
                            "min_wavelength": LAT_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": LAT_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                            "reference_url": "https://heasarc.gsfc.nasa.gov/docs/heasarc/missions/fermi.html",
                        }
                    ],
                },
            ],
        },
        {
            "name": "Gamma-ray Burst Monitor",
            "short_name": "GBM",
            "id": uuid.UUID("6fd90826-c3c9-4ad0-be01-63ed88a8f484"),
            "is_operational": True,
            "reference_url": "https://fermi.gsfc.nasa.gov",
            "instruments": [
                {
                    "name": "Gamma-ray Burst Monitor",
                    "short_name": "GBM",
                    "id": uuid.UUID("1c80c356-dc44-404f-aeba-060097a7a59d"),
                    "field_of_view": InstrumentFOV.ALL_SKY.value,
                    "footprint": [],
                    "is_operational": True,
                    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/heasarc/missions/fermi.html",
                    "type": InstrumentType.SCINTILLATOR.value,
                    "filters": [
                        {
                            "name": "Fermi GBM Bandpass",
                            "id": uuid.UUID("81f8bd53-49f6-4a17-9395-86b87c2ac9e8"),
                            "min_wavelength": GBM_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": GBM_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                            "reference_url": "https://heasarc.gsfc.nasa.gov/docs/heasarc/missions/fermi.html",
                        }
                    ],
                }
            ],
        },
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("ad78414a-1643-4ff0-9ab0-403ea51b1067"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("817a374a-5e60-4168-bb27-79a0df006c05"),
                "norad_id": 33053,
                "norad_satellite_name": "FGRST (GLAST)",
            },
        }
    ],
    "group": {
        "id": uuid.UUID("2d1919c9-728b-4d8c-8afb-ad60c63eab4e"),
        "name": "Fermi Gamma-ray Space Telescope",
        "short_name": "Fermi",
        "group_admin": {
            "id": uuid.UUID("449c19ee-7b09-4b4d-ae52-99885a37f7be"),
            "name": "Fermi Group Admin",
        },
    },
}


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    records = ssa_records.build(session, OBSERVATORY, snapshot_models)

    session.add_all(records)
    session.commit()
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    ssa_records.delete(session, OBSERVATORY, snapshot_models)

    session.commit()
    # ### end Alembic commands ###
