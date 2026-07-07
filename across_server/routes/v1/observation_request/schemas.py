from __future__ import annotations

import uuid

from across_server.core.date_utils import UTCDatetime
from across_server.core.schemas.base import BaseSchema
from across_server.core.schemas.pagination import PaginationParams

from ....core.enums import ObservationRequestStatus
from ....core.schemas import Coordinate, NullableEndDateRange, UnitValue
from ....db.models import ObservationRequest as ObservationRequestModel


class ObservationRequestBase(BaseSchema):
    science_justification: str
    object_name: str
    object_coordinates: Coordinate
    object_brightness: UnitValue
    observation_window: NullableEndDateRange
    exposure_time: float
    anonymize: bool
    is_too: bool
    instrument_id: uuid.UUID
    instrument_config: dict | None = None
    parent_id: uuid.UUID | None = None
    related_requests: list[ObservationRequest] | None = None


class ObservationRequestCreate(ObservationRequestBase):
    proposal_name: str | None = None
    proposal_code: str | None = None

    def to_orm(self) -> ObservationRequestModel:
        """
        Converts Pydantic schema to ORM representation
        Translates field names and flattens nested Pydantic schemas
        """
        data = self.model_dump(exclude_unset=True)

        data["id"] = uuid.uuid4()

        # default parent_id to id
        data["parent_id"] = data["parent_id"] or data["id"]

        # coordinates
        object_coords = self.object_coordinates.model_dump_with_prefix(
            prefix="object", data=self.object_coordinates.model_dump()
        )
        data.update(object_coords)
        data["object_position"] = self.object_coordinates.create_gis_point()
        del data["object_coordinates"]

        # date range
        date_range_data = self.observation_window.model_dump_with_prefix(
            prefix="date_range", data=self.observation_window.model_dump()
        )
        del data["observation_window"]
        data.update(date_range_data)

        # object brightness TODO: change `object_brightness` to `object_brightness_value`
        depth_data = self.object_brightness.model_dump_with_prefix(
            prefix="object_brightness", data=self.object_brightness.model_dump()
        )
        del data["object_brightness"]
        data.update(depth_data)

        return ObservationRequestModel(**data)


class ObservationRequestUpdate(ObservationRequestBase):
    pass


class ObservationRequestStatusUpdate(BaseSchema):
    status: ObservationRequestStatus
    status_reason: str | None = None


class ObservationRequest(ObservationRequestBase):
    id: uuid.UUID
    status: ObservationRequestStatus
    status_reason: str | None

    @classmethod
    def from_orm(
        cls, observation_request: ObservationRequestModel, include_history: bool = False
    ) -> ObservationRequest:
        return ObservationRequest(
            id=observation_request.id,
            parent_id=observation_request.parent_id,
            science_justification=observation_request.science_justification,
            object_name=observation_request.object_name,
            object_coordinates=Coordinate(
                ra=observation_request.object_ra, dec=observation_request.object_dec
            ),
            object_brightness=UnitValue(
                value=observation_request.object_brightness,
                unit=observation_request.object_brightness_unit,
            ),
            observation_window=NullableEndDateRange(
                begin=observation_request.date_range_begin,
                end=observation_request.date_range_end,
            ),
            exposure_time=observation_request.exposure_time,
            anonymize=observation_request.anonymize,
            is_too=observation_request.is_too,
            instrument_id=observation_request.instrument_id,
            instrument_config=observation_request.instrument_configuration,
            status=ObservationRequestStatus(observation_request.status),
            status_reason=observation_request.status_reason,
            related_requests=[
                ObservationRequest.from_orm(related_request, include_history=False)
                for related_request in observation_request.related_requests
            ]
            if include_history
            else None,
        )


class ObservationRequestReadParams(PaginationParams):
    observatory_names: list[str] | None = None
    observatory_ids: list[uuid.UUID] | None = None
    telescope_names: list[str] | None = None
    telescope_ids: list[uuid.UUID] | None = None
    instrument_names: list[str] | None = None
    instrument_ids: list[uuid.UUID] | None = None
    object_name: str | None = None
    object_cone_search_ra: float | None = None
    object_cone_search_dec: float | None = None
    object_cone_search_radius: float | None = None
    begin_date: UTCDatetime | None = None
    end_date: UTCDatetime | None = None
    status: ObservationRequestStatus | None = None
    proposal_name: str | None = None
    proposal_code: str | None = None
    proposal_ids: list[str] | None = None
    is_too: bool = True
    parent_id: uuid.UUID | None = None
    include_history: bool = False


class ObservationRequestBulkCreate(BaseSchema):
    """
    A Pydantic model class representing bulk observation request creation

    Parameters
    --------------
    observation_requests: list[ObservationRequestCreate]
        A list of ObservationRequestCreate objects to be added in bulk
    """

    observation_requests: list[ObservationRequestCreate]
