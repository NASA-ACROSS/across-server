import types
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase

from across_server.core.enums.ephemeris_type import EphemerisType
from migrations import db_util


def build(
    session: Any,
    observatory_data: Any,
    models: types.ModuleType,
) -> list[DeclarativeBase]:
    records: list[DeclarativeBase] = []

    # expects permission models, but these exist so they won't be created,
    # it is just for the relationship
    group_permissions = session.scalars(
        select(models.Permission).filter(models.Permission.name.contains("group"))
    ).all()

    # create the group
    group_data = observatory_data.pop("group")
    group_admin_data = group_data.pop("group_admin")
    group = models.Group(**group_data)
    records.append(group)

    # create group admin
    records.append(
        models.GroupRole(
            **group_admin_data,
            permissions=group_permissions,
            group=group,
        )
    )

    # pop needed data from observatory_data
    telescopes = observatory_data.pop("telescopes")
    ephemeris_types = observatory_data.pop("ephemeris_types")

    # create observatory
    observatory = models.Observatory(group=group, **observatory_data)
    records.append(observatory)

    # get the telescopes
    for telescope_data in telescopes:
        instruments = telescope_data.pop("instruments")
        # create the telescope record
        telescope = models.Telescope(observatory_id=observatory.id, **telescope_data)
        records.append(telescope)

        # get the instruments
        for instrument_data in instruments:
            footprints = instrument_data.pop("footprint")
            filters = instrument_data.pop("filters")

            # create the instrument record
            instrument = models.Instrument(telescope_id=telescope.id, **instrument_data)
            records.append(instrument)

            for footprint_data in footprints:
                # convert the input footprint to the string polygon
                vertices = []
                for point in footprint_data:
                    vertices.append(
                        db_util.ACROSSFootprintPoint(x=point["x"], y=point["y"])
                    )

                polygon = db_util.create_geography(polygon=vertices)

                # create the footprint model record
                footprint = models.Footprint(
                    polygon=polygon, instrument_id=instrument.id
                )
                records.append(footprint)

            for filter_data in filters:
                filter = models.Filter(instrument_id=instrument.id, **filter_data)
                records.append(filter)

    # Add Ephemeris Parameters
    for ephemeris_type_data in ephemeris_types:
        parameters = ephemeris_type_data.pop("parameters")
        ephemeris_type = models.ObservatoryEphemerisType(
            observatory_id=observatory.id,
            **ephemeris_type_data,
        )
        records.append(ephemeris_type)

        if ephemeris_type.ephemeris_type == EphemerisType.TLE:
            tle_parameters = models.TLEParameters(
                observatory_id=observatory.id, **parameters
            )
            records.append(tle_parameters)

        if ephemeris_type.ephemeris_type == EphemerisType.JPL:
            jpl_parameters = models.JPLEphemerisParameters(
                observatory_id=observatory.id, **parameters
            )
            records.append(jpl_parameters)

        if ephemeris_type.ephemeris_type == EphemerisType.SPICE:
            spice_parameters = models.SpiceKernelParameters(
                observatory_id=observatory.id, **parameters
            )
            records.append(spice_parameters)

        if ephemeris_type.ephemeris_type == EphemerisType.GROUND:
            ground_parameters = models.EarthLocationParameters(
                observatory_id=observatory.id, **parameters
            )
            records.append(ground_parameters)

    return records


def delete(session: Any, observatory_data: dict, models: types.ModuleType) -> None:
    group = session.scalar(
        select(models.Group).filter_by(id=observatory_data["group"]["id"])
    )
    session.delete(group)

    observatory = session.scalar(
        select(models.Observatory).filter_by(id=observatory_data["id"])
    )
    session.delete(observatory)

    tle_parameters = session.scalar(
        select(models.TLEParameters).filter_by(observatory_id=observatory_data["id"])  # type:ignore
    )
    if tle_parameters:
        session.delete(tle_parameters)

    jpl_parameters = session.scalar(
        select(models.JPLEphemerisParameters).filter_by(
            observatory_id=observatory_data["id"]  # type:ignore
        )
    )
    if jpl_parameters:
        session.delete(jpl_parameters)

    spice_parameters = session.scalar(
        select(models.SpiceKernelParameters).filter_by(
            observatory_id=observatory_data["id"]  # type:ignore
        )
    )
    if spice_parameters:
        session.delete(spice_parameters)

    ground_parameters = session.scalar(
        select(models.EarthLocationParameters).filter_by(
            observatory_id=observatory_data["id"]  # type:ignore
        )
    )
    if ground_parameters:
        session.delete(ground_parameters)
