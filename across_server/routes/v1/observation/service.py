from collections.abc import Sequence
from typing import Annotated, Tuple
from uuid import UUID

from across.tools import (
    EnergyBandpass,
    FrequencyBandpass,
    WavelengthBandpass,
    convert_to_wave,
)
from across.tools import enums as tools_enums
from fastapi import Depends
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.constants import EARTH_CIRCUMFERENCE_METERS_PER_DEGREE
from ....db import models
from ....db.database import get_session
from .exceptions import (
    InvalidObservationReadParametersException,
    ObservationNotFoundException,
)
from .schemas import ObservationRead


class ObservationService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get(self, observation_id: UUID) -> models.Observation:
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
        query = select(models.Observation).where(
            models.Observation.id == observation_id
        )

        result = await self.db.execute(query)
        observation = result.scalar_one_or_none()

        if observation is None:
            raise ObservationNotFoundException(observation_id)

        return observation

    def _get_observation_filter(self, data: ObservationRead) -> list:
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
                models.Observation.date_range_begin >= data.date_range_begin
            )
        if data.date_range_end:
            data_filter.append(models.Observation.date_range_end <= data.date_range_end)

        bandpass_params = [data.bandpass_min, data.bandpass_max, data.bandpass_type]
        if any(bandpass_params) and not all(bandpass_params):
            raise InvalidObservationReadParametersException(
                message="Bandpass parameters are not complete. Please provide all bandpass parameters."
            )

        elif all(bandpass_params):
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

        cone_search_params = [
            data.cone_search_ra,
            data.cone_search_dec,
            data.cone_search_radius,
        ]
        if any(cone_search_params) and not all(cone_search_params):
            raise InvalidObservationReadParametersException(
                message="Cone search parameters are not complete. Please provide all cone search parameters."
            )
        elif all(cone_search_params):
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

    async def get_many(
        self, data: ObservationRead
    ) -> Sequence[Tuple[models.Observation, int]]:
        """
        Retrieve the Observation records with the given filters.

        Parameters
        ----------
        data : schemas.ObservationRead
            the ObservationRead data

        Returns
        -------
        Sequence[models.Observation]
            The Observations within the given filters
        """
        query = (
            select(models.Observation, func.count().over().label("count"))
            .where(*self._get_observation_filter(data))
            .order_by(models.Observation.created_on.desc())
            .limit(data.page_limit)
            .offset(data.offset)
        )

        result = await self.db.execute(query)
        observations = result.tuples().all()

        return observations
