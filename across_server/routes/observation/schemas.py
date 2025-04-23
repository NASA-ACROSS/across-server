from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, ClassVar

from across.tools import EnergyBandpass, FrequencyBandpass, WavelengthBandpass
from across.tools import enums as tools_enums
from pydantic import BeforeValidator

from ...core.date_utils import convert_to_utc
from ...core.enums import (
    DepthUnit,
    IVOAObsCategory,
    IVOAObsTrackingType,
    ObservationStatus,
    ObservationType,
)
from ...core.schemas import Coordinate, DateRange, UnitValue
from ...core.schemas.bandpass import bandpass_converter
from ...core.schemas.base import (
    BaseSchema,
)
from ...db.models import Observation as ObservationModel


class ObservationBase(
    BaseSchema,
):
    instrument_id: uuid.UUID
    object_name: str
    pointing_position: Coordinate
    date_range: DateRange
    external_observation_id: str
    type: ObservationType
    status: ObservationStatus
    pointing_angle: float | None = None
    exposure_time: float | None = None
    reason: str | None = None
    description: str | None = None
    proposal_reference: str | None = None
    object_position: Coordinate | None = None
    depth: UnitValue | None = None
    bandpass: EnergyBandpass | FrequencyBandpass | WavelengthBandpass
    # Explicit IVOA ObsLocTap
    t_resolution: float | None = None
    em_res_power: float | None = None
    o_ucd: str | None = None
    pol_states: str | None = None
    pol_xel: str | None = None
    category: IVOAObsCategory | None = None
    priority: int | None = None
    tracking_type: IVOAObsTrackingType | None = None

    orm_model: ClassVar = ObservationModel


class Observation(ObservationBase):
    id: uuid.UUID
    schedule_id: uuid.UUID
    created_on: datetime
    created_by_id: uuid.UUID | None = None

    @staticmethod
    def from_orm(observation: ObservationModel) -> Observation:
        if observation.depth_unit:
            depth = UnitValue(
                unit=DepthUnit(observation.depth_unit), value=observation.depth_value
            )
        else:
            depth = None

        if observation.category:
            category = IVOAObsCategory(observation.category)
        else:
            category = None

        if observation.tracking_type:
            tracking_type = IVOAObsTrackingType(observation.tracking_type)
        else:
            tracking_type = None

        return Observation(
            id=observation.id,
            instrument_id=observation.instrument_id,
            schedule_id=observation.schedule_id,
            object_name=observation.object_name,
            pointing_position=Coordinate(
                ra=observation.pointing_ra, dec=observation.pointing_dec
            ),
            date_range=DateRange(
                begin=observation.date_range_begin, end=observation.date_range_end
            ),
            exposure_time=observation.exposure_time,
            external_observation_id=observation.external_observation_id,
            type=ObservationType(observation.type),
            status=ObservationStatus(observation.status),
            pointing_angle=observation.pointing_angle,
            reason=observation.reason,
            description=observation.description,
            proposal_reference=observation.proposal_reference,
            object_position=Coordinate(
                ra=observation.object_ra, dec=observation.object_dec
            ),
            depth=depth,
            bandpass=WavelengthBandpass(
                min=observation.min_wavelength,
                max=observation.max_wavelength,
                peak_wavelength=observation.peak_wavelength,
                filter_name=observation.filter_name,
                unit=tools_enums.WavelengthUnit.ANGSTROM,
            ),
            t_resolution=observation.t_resolution,
            em_res_power=observation.em_res_power,
            o_ucd=observation.o_ucd,
            pol_states=observation.pol_states,
            pol_xel=observation.pol_xel,
            category=category,
            priority=observation.priority,
            created_on=observation.created_on,
            tracking_type=tracking_type,
        )


class ObservationCreate(ObservationBase):
    created_on: Annotated[datetime | None, BeforeValidator(convert_to_utc)] = None
    created_by_id: uuid.UUID | None = None

    return_schema: ClassVar = Observation

    def to_orm(self) -> ObservationModel:
        """
        Converts Pydantic schema to ORM representation
        Translates field names and flattens nested Pydantic schemas
        """
        data = self.model_dump(exclude_unset=True)

        pointing_coords = self.pointing_position.model_dump_with_prefix(
            prefix="pointing", data=self.pointing_position.model_dump()
        )
        pointing_position_element = self.pointing_position.create_gis_point()

        if self.object_position:
            object_coords = self.object_position.model_dump_with_prefix(
                prefix="object", data=self.object_position.model_dump()
            )
            object_position_element = self.object_position.create_gis_point()
            data.update(object_coords)

        if self.depth:
            depth_data = self.depth.model_dump_with_prefix(
                prefix="depth", data=self.depth.model_dump()
            )
            del data["depth"]
            data.update(depth_data)

        date_range_data = self.date_range.model_dump_with_prefix(
            prefix="date_range", data=self.date_range.model_dump()
        )
        del data["date_range"]

        for obj in [pointing_coords, date_range_data]:
            data.update(obj)

        data["pointing_position"] = pointing_position_element
        if self.object_position:
            data["object_position"] = object_position_element

        bandpass = bandpass_converter(self.bandpass)
        data["filter_name"] = bandpass.filter_name
        data["min_wavelength"] = bandpass.min
        data["max_wavelength"] = bandpass.max
        data["peak_wavelength"] = bandpass.peak_wavelength

        if "bandpass" in data.keys():
            del data["bandpass"]

        return self.orm_model(**data)
