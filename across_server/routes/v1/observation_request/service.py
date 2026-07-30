import uuid
from collections import defaultdict
from datetime import datetime
from typing import Annotated, Tuple
from uuid import UUID

from fastapi import Depends
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.core.schemas.pagination import PaginationParams
from across_server.routes.v1.observation_request.access import (
    is_admin_clause,
    is_creator_clause,
)

from ....auth.schemas import AuthUser
from ....core.constants import EARTH_CIRCUMFERENCE_METERS_PER_DEGREE
from ....db import models
from ....db.database import get_session
from . import schemas
from .exceptions import (
    InvalidObservationRequestCreateParametersException,
    InvalidObservationRequestReadParametersException,
    ObservationRequestNotFoundException,
)


class ObservationRequestService:
    """
    ObservationRequest service for managing observation requests in the ACROSS SSA system.
    This service handles CRUD operations for ObservationRequest records. This includes retrieving
    ObservationRequest records from the database, creating new ObservationRequests, modifying existing
    ObservationRequests, and checking if the ObservationRequest objects need to be redacted depending on the
    requester's group role or submitter status.

    Methods
    -------
    get(observation_request_id: UUID, auth_user: AuthUser) -> models.ObservationRequest
        Retrieve the ObservationRequest by id.
    get_many(params: schemas.ObservationRequestReadParams, auth_user: AuthUser) -> Sequence[models.ObservationRequest]
        Retrieves many ObservationRequests based on filter params.
    create(data: schemas.ObservationRequestCreate, auth_user: AuthUser) -> UUID
        Create a new ObservationRequest record
    create_many(data: schemas.ObservationRequestCreateMany, auth_user: AuthUser) -> list[UUID]
        Create many new ObservationRequest records
    modify(data: schemas.ObservationRequestPut, auth_user: AuthUser) -> models.ObservationRequest
        Modify an ObservationRequest record
    delete(observation_request_id: UUID, auth_user: AuthUser) -> UUID
        Delete an ObservationRequest record (sets status to "archived")
    get_observation_request_history(observation_request_id: UUID, auth_user: AuthUser) -> Sequence[models.ObservationRequest]
        Get the history of an ObservationRequest record by id.
    """

    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    async def get(
        self,
        observation_request_id: UUID,
        auth_user: AuthUser | None,
    ) -> schemas.ObservationRequest:
        """
        Retrieve the ObservationRequest record with the given id.

        Parameters
        ----------
        observation_request_id : UUID
            the ObservationRequest id
        auth_user: AuthUser
            the user making the request
        Returns
        -------
        models.ObservationRequest
            The ObservationRequest with the given id
        Raises
        ------
        ObservationRequestNotFoundException
        """
        is_viewer = ~(is_creator_clause(auth_user) | is_admin_clause(auth_user))
        obs_req_select = select(
            models.ObservationRequest,
            is_viewer.label("is_viewer"),
        )

        query = obs_req_select.where(
            models.ObservationRequest.id == observation_request_id
        )

        result = await self.db.execute(query)
        observation_request, is_viewer = result.one_or_none() or (
            None,
            True,
        )

        if observation_request is None:
            raise ObservationRequestNotFoundException(observation_request_id)

        versions_query = obs_req_select.where(
            models.ObservationRequest.parent_id == observation_request.parent_id
        ).order_by(models.ObservationRequest.created_on.desc())

        versions_result = await self.db.execute(versions_query)

        versions = versions_result.tuples().all()

        observation_request = self._redact_to_schema(observation_request, is_viewer)

        observation_request.versions = [
            self._redact_to_schema(version, is_viewer)
            for version, is_viewer in versions
        ]

        return observation_request

    async def get_many(
        self,
        params: schemas.ObservationRequestReadParams,
        auth_user: AuthUser | None,
    ) -> Tuple[list[schemas.ObservationRequest], int]:
        """
        Retrieve a list of ObservationRequest records
        based on the query parameters.

        Parameters
        ----------
        params : schemas.ObservationRequestReadParams
            class representing ObservationRequest filter parameters
        auth_user: AuthUser
            the user making the request
        Returns
        -------
        list[Tuple[models.ObservationRequest, int]]
            The list of ObservationRequest records and the total number of records
            as a tuple
        """
        is_admin = is_admin_clause(auth_user)
        is_creator = is_creator_clause(auth_user)
        is_viewer = ~(is_admin | is_creator)

        pagination_fields = set(PaginationParams.model_fields) | set(
            PaginationParams.model_computed_fields
        )
        req_params = list(
            params.model_dump(exclude_none=True, exclude=pagination_fields).keys()
        )
        only_proposal_fields = set(req_params).issubset(
            {"proposal_name", "proposal_code", "proposal_ids"}
        )

        observation_request_filter = self._get_filter(data=params)

        # if the user is a viewer and they only provide proposal information,
        # they should only see non-anonymized observation requests.
        # otherwise with other params, the observation requests will be anonymized
        if only_proposal_fields:
            observation_request_filter.append(
                or_(is_viewer, ~models.ObservationRequest.anonymize)
            )

        # get the top level observation requests (parent_id is None) based on the filters
        observation_request_query = (
            select(
                models.ObservationRequest,
                is_viewer.label("is_viewer"),
            )
            .filter(
                *observation_request_filter,
                models.ObservationRequest.parent_id.is_(None),
            )
            .order_by(
                models.ObservationRequest.created_on.desc(),
            )
            .group_by(models.ObservationRequest.id)
            .limit(params.page_limit)
            .offset(params.offset)
        )

        result = await self.db.execute(observation_request_query)
        observation_requests = list(result.tuples().all())

        # get the proposals for all requests
        proposal_query = select(models.ObservingProposal).where(
            models.ObservingProposal.id.in_(
                [
                    observation_request.proposal_id
                    for observation_request, _ in observation_requests
                    if observation_request.proposal_id is not None
                ]
            )
        )
        proposal_result = await self.db.execute(proposal_query)
        proposals = list(proposal_result.scalars().all())
        proposal_dict = {proposal.id: proposal for proposal in proposals}

        # total_count query for pagination total result set info given filters
        count_query = (
            select(func.count())
            .select_from(models.ObservationRequest)
            .where(*observation_request_filter)
        )
        total_count = (await self.db.execute(count_query)).scalar_one()

        redacted_observation_requests: list[schemas.ObservationRequest] = []

        for observation_request, is_viewer in observation_requests:
            if observation_request.proposal_id is not None:
                proposal = proposal_dict.get(observation_request.proposal_id)

            redacted_observation_request = self._redact_to_schema(
                observation_request, is_viewer, proposal
            )
            redacted_observation_requests.append(redacted_observation_request)

        if params.include_versions:
            versions = await self._get_versions(observation_requests, proposal_dict)

            # build lookup of grouped versions (already sorted in descending order by created_on)
            grouped_versions = defaultdict(list)
            for version in versions:
                grouped_versions[version.parent_id].append(version)

            for req in redacted_observation_requests:
                req.versions = grouped_versions.get(req.id, [])

        return redacted_observation_requests, total_count

    async def create(
        self, data: schemas.ObservationRequestCreate, created_by_id: UUID
    ) -> UUID:
        """
        Create a new ObservationRequest record in the database.

        Parameters
        -----------
        data : schemas.ObservationRequestCreate
            The ObservationRequest to be created.
        created_by_id: UUID
            the ID of the submitter
        Returns
        -------
        UUID:
            The id of the newly created ObservationRequest
        """
        await self._can_submit([data.instrument_id])
        await self._assign_proposal_ids([data])

        observation_request = data.to_orm(created_by_id)

        self.db.add(observation_request)

        return observation_request.id

    async def create_many(
        self, data: schemas.ObservationRequestCreateMany, created_by_id: UUID
    ) -> list[UUID]:
        """
        Create many new ObservationRequest records in the database.

        Parameters
        -----------
        data : schemas.ObservationRequestCreateMany
            The ObservationRequests to be created.
        created_by_id: UUID
            the ID of the submitter
        Returns
        -------
        list[UUID]:
            The ids of the newly created ObservationRequests
        """
        # Error if an instrument does not allow observation requests
        instrument_ids = [req.instrument_id for req in data.observation_requests]
        await self._can_submit(instrument_ids)

        creates_with_proposals = list(
            filter(
                lambda observation_request: observation_request.proposal is not None,
                data.observation_requests,
            )
        )

        await self._assign_proposal_ids(creates_with_proposals)

        # Bulk add the ObservationRequest records to the database
        observation_request_records: list[models.ObservationRequest] = []
        for observation_request_create in data.observation_requests:
            record = observation_request_create.to_orm(created_by_id)
            observation_request_records.append(record)

        self.db.add_all(observation_request_records)
        await self.db.commit()

        return [req.id for req in observation_request_records]

    async def modify(
        self,
        parent_id: UUID,
        data: schemas.ObservationRequestUpdate,
        modified_by_id: UUID,
    ) -> UUID:
        """
        Modify an ObservationRequest given some changes.
        Upon modification, a new ObservationRequest is created with the changes,
        with the same parent_id as the original ObservationRequest.

        Parameters
        ----------
        parent_id: UUID
            the ID of the parent ObservationRequest to modify
        data : schemas.ObservationRequestUpdate
            the changes to the ObservationRequest
        modified_by_id: UUID
            the ID of the user making the request
        Returns
        -------
        models.ObservationRequest
            The ObservationRequest with the modifications
        """

        parent_query = select(models.ObservationRequest).where(
            models.ObservationRequest.id == parent_id
        )
        parent_result = await self.db.execute(parent_query)
        parent_observation_request = parent_result.scalar_one_or_none()

        if parent_observation_request is None:
            raise ObservationRequestNotFoundException(parent_id)

        # set the parent_id of the new ObservationRequest to the parent ObservationRequest's id
        data.parent_id = parent_observation_request.id

        update_id = await self.create(data, created_by_id=modified_by_id)

        # Anonymize all existing versions if the newest version is changing anonymization
        if data.anonymize != parent_observation_request.anonymize:
            versions_query = select(models.ObservationRequest).where(
                models.ObservationRequest.parent_id == parent_id
            )
            result = await self.db.execute(versions_query)
            versions = result.scalars().all()
            for version in versions:
                version.anonymize = data.anonymize

        return update_id

    async def update_status(
        self,
        observation_request_id: UUID,
        data: schemas.ObservationRequestStatusUpdate,
        modified_by_id: UUID,
    ) -> UUID:
        """
        Update the status of an ObservationRequest by ID.

        Parameters
        ----------
        observation_request_id : UUID
            the ObservationRequest ID
        data: schemas.ObservationRequestStatusUpdate
            the new status and reason for the ObservationRequest
        modified_by_id: UUID
            the UUID of the user updating the ObservationRequest
        Returns
        -------
        UUID
            The ID of the updated ObservationRequest
        """
        query = select(models.ObservationRequest).where(
            models.ObservationRequest.id == observation_request_id
        )
        result = await self.db.execute(query)
        observation_request = result.scalar_one_or_none()

        if observation_request is None:
            raise ObservationRequestNotFoundException(observation_request_id)

        observation_request.status = data.status
        observation_request.status_reason = data.status_reason
        observation_request.modified_by_id = modified_by_id
        observation_request.modified_on = datetime.now()

        await self.db.commit()

        return observation_request.id

    def _get_filter(self, data: schemas.ObservationRequestReadParams) -> list:
        """
        Build the sqlalchemy filter list based on the passed in ObservationRequestReadParams.
        Parses whether or not any of the fields are populated, and constructs a list
        of sqlalchemy filter booleans for the ObservationRequests.

        Parameters
        ----------
        data: schemas.ObservationRequestReadParams
            class representing ObservationRequest filter parameters

        Returns
        -------
        list[sqlalchemy.filters]
            list of ObservationRequest filter booleans
        """
        data_filter: list = []

        if data.ids and len(data.ids):
            data_filter.append(models.ObservationRequest.id.in_(data.ids))

        if data.observatory_ids and len(data.observatory_ids):
            data_filter.append(
                models.ObservationRequest.instrument.has(
                    models.Instrument.telescope.has(
                        models.Telescope.observatory_id.in_(data.observatory_ids)
                    )
                )
            )

        if data.observatory_names and len(data.observatory_names):
            observatory_name_or_filter = []

            for observatory_name in data.observatory_names:
                observatory_name_or_filter.append(
                    models.ObservationRequest.instrument.has(
                        models.Instrument.telescope.has(
                            models.Telescope.observatory.has(
                                func.lower(models.Observatory.name).contains(
                                    str.lower(observatory_name)
                                )
                            )
                        )
                    )
                )

                observatory_name_or_filter.append(
                    models.ObservationRequest.instrument.has(
                        models.Instrument.telescope.has(
                            models.Telescope.observatory.has(
                                func.lower(models.Observatory.short_name).contains(
                                    str.lower(observatory_name)
                                )
                            )
                        )
                    )
                )

            data_filter.append(or_(*observatory_name_or_filter))

        if data.telescope_ids and len(data.telescope_ids):
            data_filter.append(
                models.ObservationRequest.instrument.has(
                    models.Telescope.id.in_(data.telescope_ids)
                )
            )

        if data.telescope_names and len(data.telescope_names):
            telescope_name_or_filter = []

            for telescope_name in data.telescope_names:
                telescope_name_or_filter.append(
                    models.ObservationRequest.instrument.has(
                        models.Instrument.telescope.has(
                            func.lower(models.Telescope.name).contains(
                                str.lower(telescope_name)
                            )
                        )
                    )
                )

                telescope_name_or_filter.append(
                    models.ObservationRequest.instrument.has(
                        models.Instrument.telescope.has(
                            func.lower(models.Telescope.short_name).contains(
                                str.lower(telescope_name)
                            )
                        )
                    )
                )

            data_filter.append(or_(*telescope_name_or_filter))

        if data.instrument_ids and len(data.instrument_ids):
            data_filter.append(
                models.ObservationRequest.instrument_id.in_(data.instrument_ids)
            )

        if data.instrument_names and len(data.instrument_names):
            instrument_name_or_filter = []

            for instrument_name in data.instrument_names:
                instrument_name_or_filter.append(
                    models.ObservationRequest.instrument.has(
                        func.lower(models.Instrument.name).contains(
                            str.lower(instrument_name)
                        )
                    )
                )

                instrument_name_or_filter.append(
                    models.ObservationRequest.instrument.has(
                        func.lower(models.Instrument.short_name).contains(
                            str.lower(instrument_name)
                        )
                    )
                )

            data_filter.append(or_(*instrument_name_or_filter))

        if data.object_name:
            data_filter.append(
                func.lower(models.ObservationRequest.object_name).contains(
                    str.lower(data.object_name)
                )
            )

        cone_search_params = [
            data.object_cone_search_ra,
            data.object_cone_search_dec,
            data.object_cone_search_radius,
        ]
        if any(param is not None for param in cone_search_params) and not all(
            param is not None for param in cone_search_params
        ):
            raise InvalidObservationRequestReadParametersException(
                message="Cone search parameters are not complete. Please provide all cone search parameters."
            )
        elif all(param is not None for param in cone_search_params):
            cone_search_point = from_shape(
                Point(data.object_cone_search_ra, data.object_cone_search_dec),  # type: ignore
                srid=4326,
            )

            # Convert degrees to meters
            cone_search_radius = (
                data.object_cone_search_radius * EARTH_CIRCUMFERENCE_METERS_PER_DEGREE  # type: ignore
            )

            data_filter.append(
                ST_DWithin(
                    models.ObservationRequest.object_position,
                    cone_search_point,
                    cone_search_radius,
                )
            )

        if data.begin_date:
            data_filter.append(
                models.ObservationRequest.date_range_end > data.begin_date
            )

        if data.end_date:
            data_filter.append(
                models.ObservationRequest.date_range_begin < data.end_date
            )

        if data.proposal_name:
            data_filter.append(
                models.ObservationRequest.observing_proposal.has(
                    func.lower(models.ObservingProposal.name).contains(
                        str.lower(data.proposal_name)
                    )
                )
            )

        if data.proposal_code:
            data_filter.append(
                models.ObservationRequest.observing_proposal.has(
                    func.lower(models.ObservingProposal.code).contains(
                        str.lower(data.proposal_code)
                    )
                )
            )

        if data.proposal_ids and len(data.proposal_ids):
            data_filter.append(
                models.ObservationRequest.proposal_id.in_(data.proposal_ids)
            )

        if data.is_too is not None:
            data_filter.append(models.ObservationRequest.is_too == data.is_too)

        if data.parent_id is not None:
            data_filter.append(models.ObservationRequest.parent_id == data.parent_id)

        if data.status is not None:
            data_filter.append(models.ObservationRequest.status == data.status.value)

        return data_filter

    def _redact_to_schema(
        self,
        observation_request: models.ObservationRequest,
        is_viewer: bool,
        proposal: models.ObservingProposal | None = None,
    ) -> schemas.ObservationRequest:
        """
        Redact the ObservationRequest if the auth user is a viewer.

        Parameters
        ----------
        observation_request : models.ObservationRequest
            the ObservationRequest to redact
        is_viewer: bool
            whether the user making the request is a viewer
        Returns
        -------
        schemas.ObservationRequest
            The redacted ObservationRequest
        """

        schema = schemas.ObservationRequest.from_orm(observation_request)

        if schema.anonymize and is_viewer:
            # Redact the fields that should not be visible to viewers when anonymized
            schema.created_by_id = None
        elif proposal is not None:
            # add the proposal to the schema if it exists and the user is not a viewer
            schema.proposal = schemas.ObservingProposal.model_validate(proposal)

        return schema

    async def _get_versions(
        self,
        observation_requests: list[tuple[models.ObservationRequest, bool]],
        proposal_dict: dict[UUID, models.ObservingProposal],
    ) -> list[schemas.ObservationRequest]:
        """
        Get the versions of the ObservationRequests.

        Parameters
        ----------
        observation_requests : list[tuple[models.ObservationRequest, bool]]
            The ObservationRequests to get the versions for, along with a boolean indicating if the user is a viewer.

        Returns
        -------
        list[schemas.ObservationRequest]
            The versions of the ObservationRequests.
        """

        parent_ids = list(
            set(
                [
                    (observation_request.id, is_viewer)
                    for observation_request, is_viewer in observation_requests
                ]
            )
        )

        related_request_query = (
            select(models.ObservationRequest).where(
                models.ObservationRequest.parent_id.in_(parent_ids),
            )
        ).order_by(
            models.ObservationRequest.created_on.desc(),
        )

        versions_result = await self.db.execute(related_request_query)
        versions = versions_result.scalars().all()

        # match the is_viewer value for each version based on the parent_id of the version
        is_viewer_dict = {parent_id: is_viewer for parent_id, is_viewer in parent_ids}

        redacted_versions: list[schemas.ObservationRequest] = []

        for version in versions:
            if version.proposal_id is not None:
                proposal = proposal_dict.get(version.proposal_id)

            redacted_version = self._redact_to_schema(
                version, is_viewer_dict[version.parent_id], proposal
            )
            redacted_versions.append(redacted_version)

        return redacted_versions

    async def _can_submit(self, instrument_ids) -> None:
        """
        Check against instruments to ensure that they all have observation requests enabled.

        Parameters
        ----------
        instrument_ids : list[int]
            The IDs of the instruments to check

        Raises
        ------
        InvalidObservationRequestCreateParametersException
            If any instrument does not have observation requests enabled.
        """
        instrument_query = select(models.Instrument).where(
            models.Instrument.id.in_(instrument_ids)
        )
        result = await self.db.execute(instrument_query)
        instruments = result.scalars().all()

        # if one instrument does not have observation requests enabled but the others do,
        # we deny all create requests in the call
        can_submit_to_instruments = all(
            instrument.is_observation_request_enabled for instrument in instruments
        )

        if not can_submit_to_instruments:
            raise InvalidObservationRequestCreateParametersException(
                message="One or more instruments do not allow observation requests."
            )

    async def _assign_proposal_ids(
        self, requests: list[schemas.ObservationRequestCreate]
    ) -> None:
        """
        Handle the proposals for the observation requests.
        Finds any existing proposals or creates new proposals
        and associates them with the observation requests.

        This method modifies the observation requests in place, assigning the appropriate proposal IDs.

        Parameters
        ----------
        requests : list[schemas.ObservationRequestCreate]
            The observation requests to handle proposals for.
        Returns
        -------
        None
        """
        proposals = [
            observation_request.proposal
            for observation_request in requests  # type: ignore (we've already filtered)
        ]
        existing_proposal_records = await self._get_proposals(proposals)  # type: ignore (we've already filtered)
        existing_proposals_dict = {
            proposal.name: proposal for proposal in existing_proposal_records
        }

        new_proposals: list[schemas.ObservingProposalCreate] = []

        for request_create in requests:
            # will fail if proposal is None, but we already filtered for that above
            assert request_create.proposal is not None

            proposal_name = request_create.proposal.name
            existing_proposal = existing_proposals_dict.get(proposal_name)

            # set existing proposal to new obs_req, or create a new proposal
            if existing_proposal:
                request_create.proposal.id = existing_proposal.id
            else:
                new_proposal = schemas.ObservingProposalCreate(
                    **request_create.proposal.model_dump(),
                    id=uuid.uuid4(),
                )
                new_proposals.append(new_proposal)
                request_create.proposal.id = new_proposal.id

        await self._create_proposals(new_proposals)

    async def _get_proposals(self, proposals: list[schemas.ObservingProposal]):
        query = select(models.ObservingProposal).where(
            models.ObservingProposal.name.in_([proposal.name for proposal in proposals])
        )
        result = await self.db.execute(query)
        proposal_records = result.scalars().all()

        return list(proposal_records)

    async def _create_proposals(
        self, proposals: list[schemas.ObservingProposalCreate]
    ) -> list[models.ObservingProposal]:
        proposal_records = [
            models.ObservingProposal(**proposal.model_dump(exclude_unset=True))
            for proposal in proposals
        ]

        self.db.add_all(proposal_records)
        await self.db.flush()
        return proposal_records
