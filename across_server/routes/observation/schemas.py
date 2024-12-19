from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict

from ...db.enums import (
    ObservationType, 
    ObservationStatus,
    IVOAObsCategory,
    IVOAObsTrackingType
)
from ...db.models import Observation
from ...core.schemas import UnitValue, Coordinate, Bandpass, DateRange


class ObservationBase(BaseModel):
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

    model_config = ConfigDict(orm_model=Observation)

    def to_orm(self):
        data = self.model_dump(exclude_unset=True)

        for key in ["pointing", "object"]:
            for coord in ["ra", "dec"]:
                data[key + "_" + coord] = data.get(
                    key + "_position", 
                    {}
                ).get(coord, None)
            if key + "_position" in data.keys():
                del data[key + "_position"]

        for key, val in data.get("depth", {}).items():
            data["depth_" + key] = val
            if "depth" in data.keys():
                del data["depth"]

        for key, val in data.get("bandpass", {}).items():
            data[key] = val
            if "bandpass" in data.keys():
                del data["bandpass"]

        for key, val in data.get("date_range", {}).items():
            data["date_range_" + key] = val
            if "date_range" in data.keys():
                del data["date_range"]

        return self.model_config["orm_model"](**data)
    
    def from_orm(self, observation: Observation):

        return self.model_validate(
            {
                **observation.__dict__,
                "pointing_position": {
                    "ra": observation.pointing_ra, 
                    "dec": observation.pointing_dec
                },
                "object_position": {
                    "ra": observation.object_ra,
                    "dec": observation.object_dec
                },
                "date_range": {
                    "begin": observation.date_range_begin,
                    "end": observation.date_range_end
                },
                "depth": {
                    "value": observation.depth_value,
                    "unit": observation.depth_unit
                },
                "bandpass": {
                    "filter_name": observation.filter_name,
                    "central_wavelength": observation.central_wavelength,
                    "bandwidth": observation.bandwidth
                }
            }
        )


class Observation(ObservationBase):
    id: uuid.UUID

    # https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances
    model_config = ConfigDict(from_attributes=True)


class ObservationCreate(ObservationBase):
    pass