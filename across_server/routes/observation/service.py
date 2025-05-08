from collections.abc import Sequence
from math import cos, radians, sin
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
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import models
from ...db.database import get_session
from .exceptions import ObservationNotFoundException
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

        if data.date_range:
            if data.date_range.begin:
                data_filter.append(
                    models.Observation.date_range_begin >= data.date_range.begin
                )
            if data.date_range.end:
                data_filter.append(
                    models.Observation.date_range_end <= data.date_range.end
                )

        if data.bandpass:
            if data.bandpass.type in tools_enums.WavelengthUnit:
                wavelength_bandpass = WavelengthBandpass(
                    min=data.bandpass.min,
                    max=data.bandpass.max,
                    unit=tools_enums.WavelengthUnit(data.bandpass.type.value),
                )

            elif data.bandpass.type in tools_enums.EnergyUnit:
                energy_bandpass = EnergyBandpass(
                    min=data.bandpass.min,
                    max=data.bandpass.max,
                    unit=tools_enums.EnergyUnit(data.bandpass.type.value),
                )
                wavelength_bandpass = convert_to_wave(energy_bandpass)

            elif data.bandpass.type in tools_enums.FrequencyUnit:
                frequency_bandpass = FrequencyBandpass(
                    min=data.bandpass.min,
                    max=data.bandpass.max,
                    unit=tools_enums.FrequencyUnit(data.bandpass.type.value),
                )
                wavelength_bandpass = convert_to_wave(frequency_bandpass)

            data_filter.append(
                models.Observation.min_wavelength >= wavelength_bandpass.min
            )

            data_filter.append(
                models.Observation.max_wavelength <= wavelength_bandpass.max
            )

        if data.cone_search:
            # Convert to radians
            dec_rad = radians(data.cone_search.dec)
            cos_radius = cos(radians(data.cone_search.radius))

            # SQL expression for angular distance
            cos_angular_distance = func.sin(
                func.radians(models.Observation.pointing_dec)
            ) * sin(dec_rad) + func.cos(
                func.radians(models.Observation.pointing_ra)
            ) * cos(dec_rad) * func.cos(
                func.radians(models.Observation.pointing_ra - data.cone_search.ra)
            )

            data_filter.append(cos_angular_distance >= cos_radius)

        if data.type:
            data_filter.append(models.Observation.type == data.type.value)

        if data.depth:
            data_filter.append(models.Observation.depth_unit == data.depth.unit.value)
            data_filter.append(models.Observation.depth_value >= data.depth.value)

        return data_filter

    async def get_many(self, data: ObservationRead) -> Sequence[models.Observation]:
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
            select(models.Observation)
            .where(*self._get_observation_filter(data))
            .order_by(models.Observation.created_on.desc())
        )

        result = await self.db.execute(query)
        observations = result.scalars().all()

        return observations
