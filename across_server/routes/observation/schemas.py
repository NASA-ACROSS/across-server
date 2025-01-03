from typing import Annotated, Optional
import uuid
from pydantic import BaseModel, BeforeValidator, ConfigDict, model_validator
from datetime import datetime

from across_server.core.date_utils import convert_to_utc

from ...core.enums import (
    ObservationType, 
    ObservationStatus,
    IVOAObsCategory,
    IVOAObsTrackingType
)
from ...db.models import Observation as ObservationModel
from ...core.schemas import UnitValue, Coordinate, Bandpass, DateRange
from ...core.schemas.base import (
    CoordinateConverterMixin, 
    DateRangeConverterMixin,
    UnitValueConverterMixin,
    BandpassConverterMixin
)


class ObservationBase(
    BaseModel, 
    CoordinateConverterMixin,
    DateRangeConverterMixin,
    UnitValueConverterMixin,
    BandpassConverterMixin
):
    instrument_id: uuid.UUID 
    schedule_id: uuid.UUID
    object_name: str
    pointing_position: Coordinate
    date_range: DateRange
    external_observation_id: str
    type: ObservationType
    status: ObservationStatus
    pointing_angle: Optional[float] = None
    exposure_time: Optional[float] = None
    reason: Optional[str] = None
    description: Optional[str] = None
    proposal_reference: Optional[str] = None
    object_position: Optional[Coordinate] = None
    pointing_angle: Optional[float] = None
    depth: Optional[UnitValue] = None
    bandpass: Optional[Bandpass] = None
    #Explicit IVOA ObsLocTap
    t_resolution: Optional[float] = None
    em_res_power: Optional[float] = None
    o_ucd: Optional[str] = None
    pol_states: Optional[str] = None
    pol_xel: Optional[str] = None
    category: Optional[IVOAObsCategory] = None
    priority: Optional[int] = None
    tracking_type: Optional[IVOAObsTrackingType] = None

    model_config = ConfigDict(orm_model=ObservationModel)

    def to_orm(self):
        """
        Converts Pydantic schema to ORM representation
        Translates field names and flattens nested Pydantic schemas
        """
        data = self.model_dump(exclude_unset=True)

        pointing_coords = self.pointing_position.model_dump_with_prefix(prefix="pointing")
        pointing_position_element = self.pointing_position.create_gis_point()

        if self.object_position:
            object_coords = self.object_position.model_dump_with_prefix(prefix="object")
            object_position_element = self.object_position.create_gis_point()
            data.update(object_coords)

        if self.depth:
            depth_data = self.depth.model_dump_with_prefix(prefix="depth")
            del data["depth"]
            data.update(depth_data)
        
        date_range_data = self.date_range.model_dump_with_prefix(prefix="date_range")
        del data["date_range"]

        for key, val in data.get("bandpass", {}).items():
            data[key] = val
            if "bandpass" in data.keys():
                del data["bandpass"]

        for obj in [pointing_coords, date_range_data]:
            data.update(obj)

        data['pointing_position'] = pointing_position_element
        if self.object_position:
            data['object_position'] = object_position_element

        return self.model_config["orm_model"](**data)
    
    @model_validator(mode="before")
    def nest_flattened_jsons(cls, values):
        """
        Converts flat JSON representation of database model
        to nested JSON needed for Pydantic validation
        """
        values = cls.coordinate_converter(cls, values)
        
        if "date_range" not in values.keys():
            values = cls.date_range_converter(cls, values, "date_range")
        
        if "depth" not in values.keys():
            values = cls.unit_value_converter(cls, values, "depth")
        
        if "bandpass" not in values.keys():
            values = cls.bandpass_converter(cls, values, "bandpass")
        
        return values


class Observation(ObservationBase):
    id: uuid.UUID
    created_on: datetime
    modified_on: Optional[datetime] = None
    created_by_id: Optional[uuid.UUID] = None
    modified_on_id: Optional[uuid.UUID] = None

    # https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances
    model_config = ConfigDict(from_attributes=True)


class ObservationCreate(ObservationBase):
    created_on: Annotated[datetime, BeforeValidator(convert_to_utc)]
    created_by_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(return_schema=Observation)