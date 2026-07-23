import typing
from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from across.tools import (
    EnergyBandpass,
    FrequencyBandpass,
    WavelengthBandpass,
    convert_to_wave,
)
from across.tools import enums as tools_enums
from fastapi import Depends
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Contains, ST_DWithin
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from ....core.constants import EARTH_CIRCUMFERENCE_METERS_PER_DEGREE
from ....db import models
from ....db.database import get_session
from .exceptions import (
    InvalidObservationReadParametersException,
    ObservationNotFoundException,
)
from .schemas import ContainsPointReadParams, ObservationRead, ObservationReadBase


class ObservationService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get(
        self, observation_id: UUID, include_footprints: bool = False
    ) -> models.Observation:
        """
        Retrieve the Observation record with the given id.

        Parameters
        ----------
        observation_id : UUID
            the observation id

        Returns
        -------
        models.Observation
            The Observation with the given id

        Raises
        ------
        ObservationNotFoundException
            If the Observation with the given id does not exist
        """
        query_options = self._get_observation_query_options(include_footprints)
        query = (
            select(models.Observation)
            .where(models.Observation.id == observation_id)
            .options(query_options)  # type: ignore
        )

        result = await self.db.execute(query)
        observation = result.scalar_one_or_none()

        if observation is None:
            raise ObservationNotFoundException(observation_id)

        return observation

    def _get_observation_base_filter(
        self,
        data: ObservationReadBase,
        resolved_instrument_ids: set[UUID] | None = None,
    ) -> list:
        """
        Retrieve the Observation record with the given checksum.

        Parameters
        ----------
        data : schemas.ObservationRead
            the ObservationRead data

        Returns
        -------
        list
            returns a list of filters for the Observation record
        """
        data_filter = []

        if data.external_id:
            data_filter.append(
                func.lower(models.Observation.external_observation_id).contains(
                    str.lower(data.external_id)
                )
            )

        if data.schedule_ids:
            data_filter.append(models.Observation.schedule_id.in_(data.schedule_ids))

        if resolved_instrument_ids is not None:
            if resolved_instrument_ids:
                data_filter.append(
                    models.Observation.instrument_id.in_(list(resolved_instrument_ids))
                )
        else:
            if data.observatory_ids:
                data_filter.append(
                    models.Observation.schedule.has(
                        models.Schedule.telescope.has(
                            models.Telescope.observatory_id.in_(data.observatory_ids)
                        )
                    )
                )

            if data.telescope_ids:
                data_filter.append(
                    models.Observation.schedule.has(
                        models.Schedule.telescope_id.in_(data.telescope_ids)
                    )
                )

            if data.instrument_ids:
                data_filter.append(
                    models.Observation.instrument_id.in_(data.instrument_ids)
                )

        if data.status:
            data_filter.append(models.Observation.status == data.status.value)

        if data.proposal:
            data_filter.append(
                func.lower(models.Observation.proposal_reference).contains(
                    str.lower(data.proposal)
                )
            )

        if data.object_name:
            data_filter.append(
                func.lower(models.Observation.object_name).contains(
                    str.lower(data.object_name)
                )
            )

        if data.date_range_begin:
            data_filter.append(
                models.Observation.date_range_end >= data.date_range_begin
            )
        if data.date_range_end:
            data_filter.append(
                models.Observation.date_range_begin <= data.date_range_end
            )

        bandpass_params = [data.bandpass_min, data.bandpass_max, data.bandpass_type]
        if any(param is not None for param in bandpass_params) and not all(
            param is not None for param in bandpass_params
        ):
            raise InvalidObservationReadParametersException(
                message="Bandpass parameters are not complete. Please provide all bandpass parameters."
            )

        elif all(param is not None for param in bandpass_params):
            try:
                if data.bandpass_type in tools_enums.WavelengthUnit:
                    wavelength_bandpass = WavelengthBandpass(
                        min=data.bandpass_min,
                        max=data.bandpass_max,
                        unit=tools_enums.WavelengthUnit(data.bandpass_type.value),  # type: ignore
                    )

                elif data.bandpass_type in tools_enums.EnergyUnit:
                    energy_bandpass = EnergyBandpass(
                        min=data.bandpass_min,
                        max=data.bandpass_max,
                        unit=tools_enums.EnergyUnit(data.bandpass_type.value),  # type: ignore
                    )
                    wavelength_bandpass = convert_to_wave(energy_bandpass)

                elif data.bandpass_type in tools_enums.FrequencyUnit:
                    frequency_bandpass = FrequencyBandpass(
                        min=data.bandpass_min,
                        max=data.bandpass_max,
                        unit=tools_enums.FrequencyUnit(data.bandpass_type.value),  # type: ignore
                    )
                    wavelength_bandpass = convert_to_wave(frequency_bandpass)

            except Exception as e:
                raise InvalidObservationReadParametersException(
                    message=f"Invalid bandpass parameters: {e}"
                )
            data_filter.append(
                models.Observation.min_wavelength >= wavelength_bandpass.min
            )

            data_filter.append(
                models.Observation.max_wavelength <= wavelength_bandpass.max
            )

        if data.type:
            data_filter.append(models.Observation.type == data.type.value)

        depth_params = [data.depth_value, data.depth_unit]
        if any(depth_params) and not all(depth_params):
            raise InvalidObservationReadParametersException(
                message="Depth parameters are not complete. Please provide all depth parameters."
            )
        elif all(depth_params):
            data_filter.append(models.Observation.depth_unit == data.depth_unit.value)  # type: ignore
            data_filter.append(models.Observation.depth_value <= data.depth_value)

        return data_filter

    def _get_cone_search_filter(self, data: ObservationRead) -> list:
        """
        Retrieve the Observation records that overlap with the requested cone search parameters.

        Parameters
        ----------
        data : schemas.ObservationRead
            the ObservationRead data

        Returns
        -------
        list
            returns a list of filters for the Observation record
        """
        data_filter = []

        cone_search_params = [
            data.cone_search_ra,
            data.cone_search_dec,
            data.cone_search_radius,
        ]
        if any(param is not None for param in cone_search_params) and not all(
            param is not None for param in cone_search_params
        ):
            raise InvalidObservationReadParametersException(
                message="Cone search parameters are not complete. Please provide all cone search parameters."
            )
        elif all(param is not None for param in cone_search_params):
            cone_search_point = from_shape(
                Point(data.cone_search_ra, data.cone_search_dec),  # type: ignore
                srid=4326,
            )

            # Convert degrees to meters
            cone_search_radius = (
                data.cone_search_radius * EARTH_CIRCUMFERENCE_METERS_PER_DEGREE  # type: ignore
            )

            data_filter.append(
                ST_DWithin(
                    models.Observation.pointing_position,
                    cone_search_point,
                    cone_search_radius,
                )
            )

        return data_filter

    def _get_observation_contains_point_filter(
        self, data: ContainsPointReadParams
    ) -> list:
        """
        Retrieve the Observation records that contain the requested point.

        Parameters
        ----------
        data : schemas.PointOverlapReadParams
            the PointOverlapReadParams data

        Returns
        -------
        list
            returns a list of filters for the Observation record
        """
        data_filter = []

        coordinate_of_interest = from_shape(
            Point(data.ra, data.dec),  # type: ignore
            srid=4326,
        )

        footprint_polygon_geom = cast(
            models.ObservationFootprint.polygon,
            Geometry(geometry_type="POLYGON", srid=4326),
        )
        coordinate_of_interest_geom = cast(
            coordinate_of_interest,
            Geometry(geometry_type="POINT", srid=4326),
        )

        data_filter.append(
            models.Observation.footprints.any(
                ST_Contains(
                    footprint_polygon_geom,
                    coordinate_of_interest_geom,
                )
            )
        )

        return data_filter

    async def _get_resolved_instrument_ids(
        self, data: ObservationRead
    ) -> set[UUID] | None:
        """
        Resolve data.observatory_ids and data.telescope_ids into a list of instrument_ids

        Parameters
        ----------
        data : schemas.ObservationRead
            the ObservationRead data

        Returns
        -------
        (set[UUID] | None)
            The set of resolved instrument_ids or None
        """
        resolved_instrument_ids: set[UUID] | None = None

        if data.observatory_ids or data.telescope_ids:
            conditions = []
            if data.observatory_ids:
                conditions.append(
                    models.Telescope.observatory_id.in_(data.observatory_ids)
                )
            if data.telescope_ids:
                conditions.append(models.Telescope.id.in_(data.telescope_ids))
            result = await self.db.execute(
                select(models.Instrument.id)
                .join(
                    models.Telescope,
                    models.Instrument.telescope_id == models.Telescope.id,
                )
                .where(or_(*conditions))
            )
            resolved_instrument_ids = set(result.scalars().all())

        if data.instrument_ids:
            if resolved_instrument_ids is not None:
                resolved_instrument_ids |= set(data.instrument_ids)
            else:
                resolved_instrument_ids = set(data.instrument_ids)

        return resolved_instrument_ids

    async def get_many(
        self, data: ObservationRead
    ) -> tuple[Sequence[models.Observation], int]:
        """
        Retrieve the Observation records with the given filters.

        Parameters
        ----------
        data : schemas.ObservationRead
            the ObservationRead data

        Returns
        -------
        tuple[Sequence[models.Observation], int]
            The Observations within the given filters and the total count
        """

        query_options = self._get_observation_query_options(
            include_footprints=data.include_footprints
        )

        # pre-resolve observatory_id and telescope_id into a list of instrument_ids
        resolved_instrument_ids = await self._get_resolved_instrument_ids(data)

        query_filter = self._get_observation_base_filter(
            data, resolved_instrument_ids=resolved_instrument_ids
        ) + self._get_cone_search_filter(data)

        # total_count query for pagination total result set info given filters
        count_query = (
            select(func.count()).select_from(models.Observation).where(*query_filter)
        )
        total_count = (await self.db.execute(count_query)).scalar_one()

        # Raise when page requests out of bounds of requested data length
        if data.page and data.page_limit:
            request_total_data_start = data.page * data.page_limit

            if total_count < request_total_data_start:
                return [], total_count

        # query to find the ids quickly with indexes and leaf info
        nested_id_subq = (
            select(models.Observation.id)
            .where(*query_filter)
            .order_by(
                models.Observation.created_on.desc(), models.Observation.id.desc()
            )
            .limit(data.page_limit)
            .offset(data.offset)
            .subquery()
        )

        # hydrate the remaining info from ids returned from nested fast id retrieval
        hydrate_query = (
            select(models.Observation)
            .join(nested_id_subq, models.Observation.id == nested_id_subq.c.id)
            .options(query_options)  # type: ignore
        )

        result = await self.db.execute(hydrate_query)
        observations = typing.cast(Sequence[models.Observation], result.scalars().all())

        return observations, total_count

    def _get_observation_query_options(
        self, include_footprints: bool | None
    ) -> list[tuple]:
        if include_footprints:
            return selectinload(models.Observation.footprints)  # type: ignore

        return noload(models.Observation.footprints)  # type: ignore

    async def get_contains_point(
        self, data: ContainsPointReadParams
    ) -> tuple[Sequence[models.Observation], int]:
        """
        Retrieve the Observation records whose footprints contains a given RA/DEC.

        Parameters
        ----------
        data : schemas.PointOverlapRead
            the PointOverlapRead data

        Returns
        -------
        tuple[Sequence[models.Observation], int]
            The Observations whose footprints contain the given RA/DEC and the total count
        """

        query_options = self._get_observation_query_options(
            include_footprints=data.include_footprints
        )

        query_filter = self._get_observation_base_filter(
            data
        ) + self._get_observation_contains_point_filter(data)

        count_query = (
            select(func.count()).select_from(models.Observation).where(*query_filter)
        )
        total_count = (await self.db.execute(count_query)).scalar_one()

        data_query = (
            select(models.Observation)
            .where(*query_filter)
            .order_by(models.Observation.created_on.desc())
            .limit(data.page_limit)
            .offset(data.offset)
            .options(query_options)  # type: ignore
        )

        result = await self.db.execute(data_query)
        observations = result.scalars().all()

        return observations, total_count
