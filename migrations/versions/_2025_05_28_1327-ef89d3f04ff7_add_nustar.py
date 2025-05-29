"""add NuSTAR

Revision ID: ef89d3f04ff7
Revises: 2b00546497c1
Create Date: 2025-05-28 13:27:59.884336

"""

import uuid
from typing import Sequence, Union

from across.tools import EnergyBandpass, convert_to_wave
from across.tools.core import enums as tools_enums
from alembic import op
from sqlalchemy import orm, select

import migrations.versions.model_snapshots.models_2025_05_15 as model_snapshots
from across_server.core.enums.ephemeris_type import EphemerisType
from across_server.core.enums.instrument_fov import InstrumentFOV
from across_server.core.enums.instrument_type import InstrumentType
from across_server.core.enums.observatory_type import ObservatoryType
from migrations.db_util import ACROSSFootprintPoint, arcmin_to_deg, create_geography

# revision identifiers, used by Alembic.
revision: str = "ef89d3f04ff7"
down_revision: Union[str, None] = "2b00546497c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Table 2 of the NuSTAR observatory guide
NUSTAR_FOOTPRINT: list[list[dict]] = [
    [
        {"x": arcmin_to_deg(-6.1), "y": arcmin_to_deg(-6.1)},
        {"x": arcmin_to_deg(6.1), "y": arcmin_to_deg(-6.1)},
        {"x": arcmin_to_deg(6.1), "y": arcmin_to_deg(6.1)},
        {"x": arcmin_to_deg(-6.1), "y": arcmin_to_deg(6.1)},
        {"x": arcmin_to_deg(-6.1), "y": arcmin_to_deg(-6.1)},
    ]
]

# Table 2 of the NuSTAR observatory guide
NUSTAR_ENERGY_BANDPASS = EnergyBandpass(
    min=3.0,
    max=78.4,
    unit=tools_enums.EnergyUnit.keV,
)
NUSTAR_WAVELENGTH_BANDPASS = convert_to_wave(NUSTAR_ENERGY_BANDPASS)

OBSERVATORY = {
    "name": "Nuclear Spectroscopic Telescope Array",
    "short_name": "NuSTAR",
    "id": uuid.UUID("afc0ceca-bc57-4d38-a846-c5c36d62256a"),
    "type": ObservatoryType.SPACE_BASED.value,
    "reference_url": "https://nustar.caltech.edu",
    "is_operational": True,
    "telescopes": [
        {
            "name": "Nuclear Spectroscopic Telescope Array",
            "short_name": "NuSTAR",
            "id": uuid.UUID("281a5a5d-3629-4aa3-a739-968bee65415f"),
            "reference_url": "https://nustar.caltech.edu",
            "is_operational": True,
            "instruments": [
                {
                    "name": "Nuclear Spectroscopic Telescope Array",
                    "short_name": "NuSTAR",
                    "id": uuid.UUID("8e3f11f7-c943-4b45-b55e-59d475a4114f"),
                    "reference_url": "https://nustar.caltech.edu",
                    "field_of_view": InstrumentFOV.POLYGON.value,
                    "footprint": NUSTAR_FOOTPRINT,
                    "is_operational": True,
                    "type": InstrumentType.CALORIMETER.value,
                    "filters": [
                        {
                            "name": "NuSTAR Bandpass",
                            "id": uuid.UUID("292c3056-4e95-4bd5-9ed8-66f07e2cc809"),
                            "min_wavelength": NUSTAR_WAVELENGTH_BANDPASS.min,
                            "max_wavelength": NUSTAR_WAVELENGTH_BANDPASS.max,
                            "is_operational": True,
                        }
                    ],
                }
            ],
        }
    ],
    "ephemeris_types": [
        {
            "id": uuid.UUID("9e82750a-1b38-43ff-ab0e-05f10d8e571e"),
            "ephemeris_type": EphemerisType.TLE,
            "priority": 1,
            "parameters": {
                "id": uuid.UUID("70c7170b-443d-49cc-a38f-de20795e090d"),
                "norad_id": 38358,
                "norad_satellite_name": "NUSTAR",
            },
        }
    ],
    "group": {
        "id": uuid.UUID("98d4cabd-6dd4-48a9-a437-8e562ed3bdbd"),
        "name": "Nuclear Spectroscopic Telescope Array",
        "short_name": "NuSTAR",
        "group_admin": {
            "id": uuid.UUID("feda1a8f-2475-4092-a07e-2fd50fe76f41"),
            "name": "NuSTAR Group Admin",
        },
    },
}


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind, expire_on_commit=False)

    # create group based off the observatory
    group = OBSERVATORY.pop("group")
    group_admin = group.pop("group_admin")  # type: ignore
    group_insert = model_snapshots.Group(**group)  # type: ignore
    session.add(group_insert)

    # create group admin
    permissions = (
        session.query(model_snapshots.Permission)
        .filter(model_snapshots.Permission.name.contains("group"))
        .all()
    )
    group_admin_insert = model_snapshots.GroupRole(
        permissions=permissions, group=group_insert, **group_admin
    )
    session.add(group_admin_insert)

    telescopes = OBSERVATORY.pop("telescopes")
    ephemeris_types = OBSERVATORY.pop("ephemeris_types")

    # create observatory
    observatory_insert = model_snapshots.Observatory(group=group_insert, **OBSERVATORY)
    session.add(observatory_insert)
    observatory_id = observatory_insert.id

    # get the telescopes
    for telescope in telescopes:  #  type:ignore
        instruments = telescope.pop("instruments")
        # create the telescope record
        telescope_insert = model_snapshots.Telescope(
            observatory_id=observatory_id, **telescope
        )
        session.add(telescope_insert)
        telescope_id = telescope_insert.id

        # get the instruments
        for instrument in instruments:
            footprints = instrument.pop("footprint")
            filters = instrument.pop("filters")

            # create the instrument record
            instrument_insert = model_snapshots.Instrument(
                telescope_id=telescope_id, **instrument
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
                    polygon=polygon, instrument_id=instrument_id
                )
                session.add(footprint_insert)

            for filter in filters:
                filter_insert = model_snapshots.Filter(
                    instrument_id=instrument_id, **filter
                )
                session.add(filter_insert)

    # Add Ephemeris Parameters for Fermi
    for ephemeris_type in ephemeris_types:  # type:ignore
        # create the ephemeris type record
        parameters = ephemeris_type.pop("parameters")
        ephemeris_type_insert = model_snapshots.ObservatoryEphemerisType(
            observatory_id=observatory_id,
            **ephemeris_type,
        )
        session.add(ephemeris_type_insert)

        if ephemeris_type_insert.ephemeris_type == EphemerisType.TLE:
            tle_parameters = model_snapshots.TLEParameters(
                observatory_id=observatory_id, **parameters
            )
            session.add(tle_parameters)

        if ephemeris_type_insert.ephemeris_type == EphemerisType.JPL:
            jpl_parameters = model_snapshots.JPLEphemerisParameters(
                observatory_id=observatory_id, **parameters
            )
            session.add(jpl_parameters)

        if ephemeris_type_insert.ephemeris_type == EphemerisType.SPICE:
            spice_parameters = model_snapshots.SpiceKernelParameters(
                observatory_id=observatory_id, **parameters
            )
            session.add(spice_parameters)

        if ephemeris_type_insert.ephemeris_type == EphemerisType.GROUND:
            ground_parameters = model_snapshots.EarthLocationParameters(
                observatory_id=observatory_id, **parameters
            )
            session.add(ground_parameters)

    session.commit()
    # ### end Alembic commands ###


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    group = session.scalar(
        select(model_snapshots.Group).filter_by(name=OBSERVATORY["name"])
    )
    observatory = session.scalar(
        select(model_snapshots.Observatory).filter_by(name=OBSERVATORY["name"])
    )
    session.delete(group)
    session.delete(observatory)

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
    # ### end Alembic commands ###
