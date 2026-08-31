from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Self

from pydantic import model_validator

from ....core.date_utils import UTCDatetime
from ....core.enums import ObservationRequestStatus
from ....core.schemas import (
    Coordinate,
    NullableDateRange,
    PaginationParams,
    UnitValue,
)
from ....core.schemas.base import BaseSchema
from ....db.models import ObservationRequest as ObservationRequestModel
from ..observing_proposal.schemas import (
    ObservingProposal,
    ObservingProposalCreate,
)


class ObservationRequestBase(BaseSchema):
    science_justification: str
    object_name: str
    object_coordinates: Coordinate
    object_position_error: float | None = None
    object_brightness: UnitValue
    observation_window: NullableEndDateRange | DateRangeCreate
    exposure_time: float
    anonymize: bool
    is_too: bool  # placeholder field for the potential of general ToO request. Defaults to True right now
    instrument_id: uuid.UUID
    instrument_configuration: dict | None = None

    def _checksum(
        self, proposal: ObservingProposal | ObservingProposalCreate | None = None
    ) -> str:
        """
        Calculate a SHA-512 checksum for the observation request data.
        """
        # Serialize the relevant fields to a string representation
        instrument_config_string = (
            "".join(f"{k}{v}" for k, v in sorted(self.instrument_configuration.items()))
            if self.instrument_configuration
            else ""
        )

        proposal_string = f"{proposal.name}{proposal.code}" if proposal else ""

        data_string = (
            f"{self.science_justification}"
            f"{self.object_name}{self.object_coordinates.ra}"
            f"{self.object_coordinates.dec}{self.object_brightness.value}"
            f"{self.object_brightness.unit}{self.observation_window.begin}"
            f"{self.observation_window.end}{self.exposure_time}"
            f"{self.anonymize}{self.is_too}{self.instrument_id}"
            f"{instrument_config_string}"
            f"{proposal_string}"
        )

        return hashlib.sha512(data_string.encode()).hexdigest()


class ObservationRequestCreate(ObservationRequestBase):
    parent_id: uuid.UUID | None = None
    proposal: ObservingProposalCreate | None = None
    observation_window: DateRangeCreate

    def to_orm(self) -> ObservationRequestModel:
        """
        Converts Pydantic schema to ORM representation
        Translates field names and flattens nested Pydantic schemas
        """
        data = self.model_dump(exclude_unset=True)

        data["id"] = uuid.uuid4()

        # default parent_id to id
        if "parent_id" not in data or data["parent_id"] is None:
            data["parent_id"] = data["id"]

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

        depth_data = self.object_brightness.model_dump_with_prefix(
            prefix="object_brightness", data=self.object_brightness.model_dump()
        )
        del data["object_brightness"]

        data["object_brightness"] = depth_data["object_brightness_value"]
        data["object_brightness_unit"] = depth_data["object_brightness_unit"]

        if "proposal" in data:
            proposal = data.pop("proposal")
            data["proposal_id"] = proposal["id"]
        else:
            data["proposal_id"] = None

        return ObservationRequestModel(**data)

    @property
    def checksum(self) -> str:
        return self._checksum(proposal=self.proposal)


class ObservationRequestUpdate(ObservationRequestCreate):
    pass


class ObservationRequestStatusUpdate(BaseSchema):
    status: ObservationRequestStatus
    status_reason: str | None = None


class ObservationRequest(ObservationRequestBase):
    id: uuid.UUID
    parent_id: uuid.UUID
    status: ObservationRequestStatus
    status_reason: str | None
    proposal: ObservingProposal | None = None
    versions: list[ObservationRequest] | None = None
    created_on: datetime
    created_by_id: uuid.UUID | None
    modified_on: datetime | None
    modified_by_id: uuid.UUID | None

    @classmethod
    def from_orm(
        cls, observation_request: ObservationRequestModel
    ) -> ObservationRequest:
        return ObservationRequest(
            id=observation_request.id,
            parent_id=observation_request.parent_id,
            science_justification=observation_request.science_justification,
            object_name=observation_request.object_name,
            object_coordinates=Coordinate(
                ra=observation_request.object_ra, dec=observation_request.object_dec
            ),
            object_position_error=observation_request.object_position_error,
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
            instrument_configuration=observation_request.instrument_configuration,
            status=ObservationRequestStatus(observation_request.status),
            status_reason=observation_request.status_reason,
            proposal=ObservingProposal(
                name=observation_request.observing_proposal.name,
                code=observation_request.observing_proposal.code,
                id=observation_request.observing_proposal.id,
            )
            if observation_request.observing_proposal
            else None,
            created_on=observation_request.created_on,
            created_by_id=observation_request.created_by_id,
            modified_on=observation_request.modified_on,
            modified_by_id=observation_request.modified_by_id,
        )

    @property
    def checksum(self) -> str:
        return self._checksum(proposal=self.proposal)


class ObservationRequestReadParams(PaginationParams):
    ids: list[uuid.UUID] | None = None
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
    include_versions: bool = False


class ObservationRequestCreateMany(BaseSchema):
    """
    A Pydantic model class representing bulk observation request creation

    Parameters
    --------------
    observation_requests: list[ObservationRequestCreate]
        A list of ObservationRequestCreate objects to be added in bulk
    """

    observation_requests: list[ObservationRequestCreate]


class NullableEndDateRange(NullableDateRange):
    begin: UTCDatetime
    end: UTCDatetime | None


class DateRangeCreate(NullableEndDateRange):
    begin: UTCDatetime
    end: UTCDatetime | None

    @model_validator(mode="after")
    def validate_future_date_range(self) -> Self:
        if self.begin <= datetime.now(timezone.utc).replace(tzinfo=None):
            raise ValueError("Begin date must be in the future")

        return self

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.begin is not None and self.end is not None and self.end <= self.begin:
            raise ValueError("End date must be after begin date")

        return self
