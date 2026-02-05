from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, ClassVar

from across.tools import EnergyBandpass, FrequencyBandpass, WavelengthBandpass
from across.tools import enums as tools_enums
from pydantic import BeforeValidator, Field

from ....core.date_utils import convert_to_utc
from ....core.enums import (
    DepthUnit,
    IVOAObsCategory,
    IVOAObsTrackingType,
    ObservationStatus,
    ObservationType,
)
from ....core.enums.instrument_fov import InstrumentFOV
from ....core.exceptions import RequiredFieldException
from ....core.schemas import Coordinate, DateRange, UnitValue
from ....core.schemas.bandpass import bandpass_converter
from ....core.schemas.base import (
    BaseSchema,
)
from ....core.schemas.pagination import PaginationParams
from ....db.models import Observation as ObservationModel


class ObservationBase(
    BaseSchema,
):
    instrument_id: uuid.UUID
    object_name: str
    pointing_position: Coordinate | None = None
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

    @classmethod
    def from_orm(cls, obj: ObservationModel) -> Observation:
        if obj.depth_unit and obj.depth_value:
            depth = UnitValue[DepthUnit](
                unit=DepthUnit(obj.depth_unit), value=obj.depth_value
            )
        else:
            depth = None

        if obj.category:
            category = IVOAObsCategory(obj.category)
        else:
            category = None

        if obj.tracking_type:
            tracking_type = IVOAObsTrackingType(obj.tracking_type)
        else:
            tracking_type = None

        return cls(
            id=obj.id,
            instrument_id=obj.instrument_id,
            schedule_id=obj.schedule_id,
            object_name=obj.object_name,
            pointing_position=Coordinate(ra=obj.pointing_ra, dec=obj.pointing_dec),
            date_range=DateRange(begin=obj.date_range_begin, end=obj.date_range_end),
            exposure_time=obj.exposure_time,
            external_observation_id=obj.external_observation_id,
            type=ObservationType(obj.type),
            status=ObservationStatus(obj.status),
            pointing_angle=obj.pointing_angle,
            reason=obj.reason,
            description=obj.description,
            proposal_reference=obj.proposal_reference,
            object_position=Coordinate(ra=obj.object_ra, dec=obj.object_dec),
            depth=depth,
            bandpass=WavelengthBandpass(
                min=obj.min_wavelength,
                max=obj.max_wavelength,
                peak_wavelength=obj.peak_wavelength,
                filter_name=obj.filter_name,
                unit=tools_enums.WavelengthUnit.ANGSTROM,
            ),
            t_resolution=obj.t_resolution,
            em_res_power=obj.em_res_power,
            o_ucd=obj.o_ucd,
            pol_states=obj.pol_states,
            pol_xel=obj.pol_xel,
            category=category,
            priority=obj.priority,
            created_on=obj.created_on,
            tracking_type=tracking_type,
        )


class ObservationCreate(ObservationBase):
    created_on: Annotated[datetime | None, BeforeValidator(convert_to_utc)] = None
    created_by_id: uuid.UUID | None = None

    return_schema: ClassVar = Observation

    def to_orm(self, instrument_fov: InstrumentFOV) -> ObservationModel:
        """
        Converts Pydantic schema to ORM representation
        Translates field names and flattens nested Pydantic schemas
        """
        data = self.model_dump(exclude_unset=True)

        if (
            instrument_fov in [InstrumentFOV.POINT, InstrumentFOV.POLYGON]
            and not self.pointing_position
        ):
            raise RequiredFieldException(
                entity="observation",
                field="pointing_position",
                message=f"A pointing position is required for {InstrumentFOV.POINT.value}, and {InstrumentFOV.POLYGON.value} FOVs.",
            )

        if self.pointing_position:
            pointing_coords = self.pointing_position.model_dump_with_prefix(
                prefix="pointing", data=self.pointing_position.model_dump()
            )
            data.update(pointing_coords)

            data["pointing_position"] = self.pointing_position.create_gis_point()

        if self.object_position:
            object_coords = self.object_position.model_dump_with_prefix(
                prefix="object", data=self.object_position.model_dump()
            )
            data.update(object_coords)

            data["object_position"] = self.object_position.create_gis_point()

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
        data.update(date_range_data)

        bandpass = bandpass_converter(self.bandpass)
        data["filter_name"] = bandpass.filter_name
        data["min_wavelength"] = bandpass.min
        data["max_wavelength"] = bandpass.max
        data["peak_wavelength"] = bandpass.peak_wavelength

        if "bandpass" in data.keys():
            del data["bandpass"]

        return self.orm_model(**data)


class ObservationRead(PaginationParams):
    external_id: str | None = None
    schedule_ids: list[uuid.UUID] | None = None
    observatory_ids: list[uuid.UUID] | None = None
    telescope_ids: list[uuid.UUID] | None = None
    instrument_ids: list[uuid.UUID] | None = None
    status: ObservationStatus | None = None
    proposal: str | None = None
    object_name: str | None = None
    date_range_begin: datetime | None = None
    date_range_end: datetime | None = None
    bandpass_min: float | None = None
    bandpass_max: float | None = None
    bandpass_type: (
        tools_enums.WavelengthUnit
        | tools_enums.EnergyUnit
        | tools_enums.FrequencyUnit
        | None
    ) = None
    cone_search_ra: float | None = Field(default=None, ge=0.0, lt=360.0)
    cone_search_dec: float | None = Field(default=None, ge=-90.0, le=90.0)
    cone_search_radius: float | None = Field(default=None, gt=0.0)
    type: ObservationType | None = None
    depth_value: float | None = None
    depth_unit: DepthUnit | None = None
