"""create ixpe

Revision ID: a6590318e932
Revises: 043885e1cd78
Create Date: 2025-05-14 15:21:03.729061

"""

from __future__ import annotations

from typing import Sequence, Union
from uuid import uuid4

from across.tools import EnergyBandpass, convert_to_wave
from across.tools import enums as tools_enums
from alembic import op
from sqlalchemy import orm, select

from across_server.core.enums import EphemerisType, InstrumentFOV, InstrumentType
from migrations.db_util import ACROSSFootprintPoint, arcmin_to_deg, create_geography
from migrations.versions.model_snapshots import models_2025_05_15 as model_snapshots

# revision identifiers, used by Alembic.
revision: str = "a6590318e932"
down_revision: Union[str, None] = "043885e1cd78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
    "type": "SPACE_BASED",
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
    "ephemeris_types": [
        {
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "norad_id": 49954,
                "norad_satellite_name": "IXPE",
            },
        }
    ],
}


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    group_permissions = (
        session.query(model_snapshots.Permission)
        .filter(model_snapshots.Permission.name.contains("group"))
        .all()
    )
    # create the group
    group = model_snapshots.Group(
        id=uuid4(), name=OBSERVATORY["name"], short_name=OBSERVATORY["short_name"]
    )
    session.add(group)

    # create group admin
    group_admin = model_snapshots.GroupRole(
        id=uuid4(),
        name=f"{group.short_name} Group Admin",
        permissions=group_permissions,
        group=group,
    )
    session.add(group_admin)

    # observatory preparation
    telescopes = OBSERVATORY.pop("telescopes")
    ephemeris_types = OBSERVATORY.pop("ephemeris_types")

    # create the observatory
    observatory_insert = model_snapshots.Observatory(
        id=uuid4(),
        group=group,
        **OBSERVATORY,
    )
    session.add(observatory_insert)
    observatory_id = observatory_insert.id

    # iterate over the telescopes
    for telescope in telescopes:  #  type:ignore
        instruments = telescope.pop("instruments")

        # create the telescope record
        telescope_insert = model_snapshots.Telescope(
            id=uuid4(),
            observatory_id=observatory_id,
            **telescope,
        )
        session.add(telescope_insert)
        telescope_id = telescope_insert.id

        # get the instruments
        for instrument in instruments:
            footprints = instrument.pop("footprint")
            filters = instrument.pop("filters")

            # create the instrument record
            instrument_insert = model_snapshots.Instrument(
                id=uuid4(),
                telescope_id=telescope_id,
                **instrument,
            )
            session.add(instrument_insert)
            instrument_id = instrument_insert.id

            for footprint in footprints:
                # convert the input footprint to the string polygon
                vertices = []
                for point in footprint:
                    vertices.append(ACROSSFootprintPoint(x=point["x"], y=point["y"]))

                polygon = create_geography(polygon=vertices)

                # create the footprint model record
                footprint_insert = model_snapshots.Footprint(
                    instrument_id=instrument_id, polygon=polygon
                )
                session.add(footprint_insert)

            for filter in filters:
                # create the filters
                filter_insert = model_snapshots.Filter(
                    instrument_id=instrument_id, **filter
                )
                session.add(filter_insert)

    for ephemeris_type in ephemeris_types:  # type:ignore
        # create the ephemeris type record
        parameters = ephemeris_type.pop("parameters")
        ephemeris_type_insert = model_snapshots.ObservatoryEphemerisType(
            id=uuid4(),
            observatory_id=observatory_id,
            **ephemeris_type,
        )
        session.add(ephemeris_type_insert)

        if ephemeris_type_insert.ephemeris_type == EphemerisType.TLE:
            tle_parameters = model_snapshots.TLEParameters(
                id=uuid4(), observatory_id=observatory_id, **parameters
            )
            session.add(tle_parameters)

        if ephemeris_type_insert.ephemeris_type == EphemerisType.JPL:
            jpl_parameters = model_snapshots.JPLEphemerisParameters(
                id=uuid4(), observatory_id=observatory_id, **parameters
            )
            session.add(jpl_parameters)

        if ephemeris_type_insert.ephemeris_type == EphemerisType.SPICE:
            spice_parameters = model_snapshots.SpiceKernelParameters(
                id=uuid4(), observatory_id=observatory_id, **parameters
            )
            session.add(spice_parameters)

        if ephemeris_type_insert.ephemeris_type == EphemerisType.GROUND:
            ground_parameters = model_snapshots.EarthLocationParameters(
                id=uuid4(), observatory_id=observatory_id, **parameters
            )
            session.add(ground_parameters)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    observatory = session.scalar(
        select(model_snapshots.Observatory).filter_by(name=OBSERVATORY["name"])  # type:ignore
    )

    group = session.scalar(
        select(model_snapshots.Group).filter_by(name=observatory.name)  # type:ignore
    )

    session.delete(observatory)
    session.delete(group)

    tle_parameters = session.scalar(
        select(model_snapshots.TLEParameters).filter_by(observatory_id=observatory.id)  # type:ignore
    )
    if tle_parameters:
        session.delete(tle_parameters)

    jpl_parameters = session.scalar(
        select(model_snapshots.JPLEphemerisParameters).filter_by(
            observatory_id=observatory.id  # type:ignore
        )
    )
    if jpl_parameters:
        session.delete(jpl_parameters)

    spice_parameters = session.scalar(
        select(model_snapshots.SpiceKernelParameters).filter_by(
            observatory_id=observatory.id  # type:ignore
        )
    )
    if spice_parameters:
        session.delete(spice_parameters)

    ground_parameters = session.scalar(
        select(model_snapshots.EarthLocationParameters).filter_by(
            observatory_id=observatory.id  # type:ignore
        )
    )
    if ground_parameters:
        session.delete(ground_parameters)

    session.commit()
    # fin
