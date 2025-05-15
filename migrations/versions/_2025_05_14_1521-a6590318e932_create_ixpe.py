"""create ixpe

Revision ID: a6590318e932
Revises: 043885e1cd78
Create Date: 2025-05-14 15:21:03.729061

"""

from __future__ import annotations

import uuid
from typing import Sequence, Union
from uuid import uuid4

from across.tools import EnergyBandpass, convert_to_wave
from across.tools import enums as tools_enums
from alembic import op
from sqlalchemy import orm, select

from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from migrations.db_util import ACROSSFootprintPoint, create_geography
from migrations.versions.model_snapshots.models_2025_05_15 import (
    Filter,
    Footprint,
    Group,
    GroupRole,
    Instrument,
    Observatory,
    ObservatoryEphemerisType,
    Permission,
    Telescope,
    TLEParameters,
)

# revision identifiers, used by Alembic.
revision: str = "a6590318e932"
down_revision: Union[str, None] = "043885e1cd78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def arcmin_to_deg(arcmin: float) -> float:
    """Convert arcminute to degrees."""
    return arcmin / 60.0


# 12 arcmin x 12 arcmin square
footprint: list[list[dict]] = [
    [
        {"x": arcmin_to_deg(-6.0), "y": arcmin_to_deg(-6.0)},
        {"x": arcmin_to_deg(6.0), "y": arcmin_to_deg(-6.0)},
        {"x": arcmin_to_deg(6.0), "y": arcmin_to_deg(6.0)},
        {"x": arcmin_to_deg(-6.0), "y": arcmin_to_deg(6.0)},
        {"x": arcmin_to_deg(-6.0), "y": arcmin_to_deg(-6.0)},
    ]
]

IXPE_ENERGY_BANDPASS = EnergyBandpass(
    min=2.0,
    max=8.0,
    unit=tools_enums.EnergyUnit.keV,
)
IXPE_WAVELENGTH_BANDPASS = convert_to_wave(IXPE_ENERGY_BANDPASS)

OBSERVATORY = {
    "name": "Imaging X-Ray Polarimetry Explorer",
    "short_name": "IXPE",
    "observatory_type": "SPACE_BASED",
    "reference_url": "https://ixpe.msfc.nasa.gov/index.html",
    "is_operational": True,
    "telescopes": [
        {
            "name": "Imaging X-Ray Polarimetry Explorer",
            "short_name": "IXPE",
            "is_operational": True,
            "reference_url": "https://ixpe.msfc.nasa.gov/index.html",
            "instruments": [
                {
                    "name": "Imaging X-Ray Polarimetry Explorer",
                    "short_name": "IXPE",
                    "reference_url": "https://heasarc.gsfc.nasa.gov/docs/heasarc/missions/ixpe.html",
                    "footprint": footprint,
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "is_operational": True,
                    "type": InstrumentType.POLARIMETER.value,
                    "filters": [
                        {
                            "name": "IXPE Bandpass",
                            "min_wavelength": IXPE_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": IXPE_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                            "reference_url": "https://heasarc.gsfc.nasa.gov/docs/heasarc/missions/ixpe.html",
                        }
                    ],
                }
            ],
        }
    ],
}


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    # create group based off the observatory
    group = Group(
        id=uuid4(), name=OBSERVATORY["name"], short_name=OBSERVATORY["short_name"]
    )
    session.add(group)

    # create group admin
    permissions = (
        session.query(Permission)
        .filter(
            Permission.name.in_(
                [
                    "group:user:write",
                    "group:role:write",
                    "group:write",
                    "group:read",
                    "group:observatory:write",
                    "group:telescope:write",
                    "group:schedule:write",
                ]
            )
        )
        .all()
    )
    group_admin = GroupRole(
        id=uuid.UUID("ae1af917-093b-4b2b-a11d-cb1097470e90"),
        name="IXPE Group Admin",
        permissions=permissions,
        group=group,
    )
    session.add(group_admin)

    # # create observatory
    observatory_insert = Observatory(
        id=uuid4(),
        name=OBSERVATORY["name"],
        short_name=OBSERVATORY["short_name"],
        type=OBSERVATORY["observatory_type"],
        reference_url=OBSERVATORY["reference_url"],
        is_operational=OBSERVATORY["is_operational"],
        group=group,
    )
    session.add(observatory_insert)
    observatory_id = observatory_insert.id

    # get the telescopes
    telescopes = OBSERVATORY["telescopes"]
    for telescope in telescopes:  #  type:ignore
        # create the telescope record
        telescope_insert = Telescope(
            id=uuid4(),
            name=telescope["name"],
            short_name=telescope["short_name"],
            reference_url=telescope["reference_url"],
            is_operational=telescope["is_operational"],
            observatory_id=observatory_id,
        )
        session.add(telescope_insert)
        telescope_id = telescope_insert.id

        # get the instruments
        instruments = telescope["instruments"]  #  type:ignore
        for instrument in instruments:
            # create the instrument record
            instrument_insert = Instrument(
                id=uuid4(),
                name=instrument["name"],
                short_name=instrument["short_name"],
                type=instrument["type"],
                reference_url=instrument["reference_url"],
                is_operational=instrument["is_operational"],
                field_of_view=instrument["field_of_view"],
                telescope_id=telescope_id,
            )
            session.add(instrument_insert)
            instrument_id = instrument_insert.id

            footprints = instrument["footprint"]
            for footprint in footprints:
                # convert the input footprint to the string polygon
                vertices = []
                for point in footprint:
                    vertices.append(ACROSSFootprintPoint(x=point["x"], y=point["y"]))

                polygon = create_geography(polygon=vertices)

                # create the footprint model record
                footprint_insert = Footprint(
                    polygon=polygon, instrument_id=instrument_id
                )
                session.add(footprint_insert)

            filters = instrument["filters"]
            for filter in filters:
                filter_insert = Filter(**filter)
                filter_insert.instrument_id = instrument_id
                session.add(filter_insert)

    # Add TLEParameters for IXPE
    ephemeris_type = ObservatoryEphemerisType(
        observatory_id=observatory_id,
        ephemeris_type=EphemerisType.TLE,
        priority=1,
    )
    session.add(ephemeris_type)

    tle_parameters = TLEParameters(
        observatory_id=observatory_id,
        norad_id=49954,
        norad_satellite_name="IXPE",
    )
    session.add(tle_parameters)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    group = session.scalar(select(Group).filter_by(name=OBSERVATORY["name"]))
    observatory = session.scalar(
        select(Observatory).filter_by(name=OBSERVATORY["name"])
    )
    tle_parameters = session.scalar(
        select(TLEParameters).filter_by(observatory_id=observatory.id)  # type:ignore
    )

    session.delete(group)
    session.delete(observatory)
    session.delete(tle_parameters)

    session.commit()
    # fin
