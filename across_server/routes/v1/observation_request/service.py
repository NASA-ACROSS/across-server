import datetime
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, status
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import case, distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from ....auth.schemas import AuthUser
from ....core.constants import EARTH_CIRCUMFERENCE_METERS_PER_DEGREE
from ....core.enums.observation_request_status import ObservationRequestStatus
from ....db import models
from ....db.database import get_session
from ....util.helpers import nested
from . import schemas
from .access import is_creator_clause, is_writer_clause
from .exceptions import (
    InvalidObservationRequestCreateParametersException,
    InvalidObservationRequestReadParametersException,
    ObservationRequestConflictException,
    ObservationRequestNotFoundException,
)

type UserType = Literal["viewer", "creator", "writer"]


class ObservationRequestService:
    """
    ObservationRequest service for managing observation requests in the ACROSS SSA system.
    This service handles CRUD operations for ObservationRequest records. This includes retrieving
    ObservationRequest records from the database, creating new ObservationRequests, modifying existing
    ObservationRequests, and checking if the ObservationRequest objects need to be redacted depending on the
    requester's group role or submitter status.

    Methods
    -------
    get(observation_request_id: UUID, auth_user: AuthUser | None) -> schemas.ObservationRequest
        Retrieve the ObservationRequest by id.
    get_many(params: schemas.ObservationRequestReadParams, auth_user: AuthUser | None) -> tuple[list[schemas.ObservationRequest], int]
        Retrieves many ObservationRequests based on filter params.
    create(data: schemas.ObservationRequestCreate, created_by_id: UUID) -> UUID
        Create a new ObservationRequest record
    create_many(data: schemas.ObservationRequestCreateMany, created_by_id: UUID) -> list[UUID]
        Create many new ObservationRequest records
    modify(observation_request_id: UUID, data: schemas.ObservationRequestUpdate, modified_by_id: UUID) -> UUID
        Modify an ObservationRequest record
    update_status(observation_request_id: UUID, data: schemas.ObservationRequestStatusUpdate, modified_by_id: UUID) -> UUID
        Update the status of an ObservationRequest record.
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
        is_viewer_clause = ~(is_creator_clause(auth_user) | is_writer_clause(auth_user))

        observation_request_query = select(
            models.ObservationRequest,
            is_viewer_clause.label("is_viewer"),
        ).where(models.ObservationRequest.id == observation_request_id)

        result = await self.db.execute(observation_request_query)

        observation_request, is_viewer = result.one_or_none() or (
            None,
            True,
        )

        if observation_request is None:
            raise ObservationRequestNotFoundException(observation_request_id)

        observation_request_schema = self._redact_to_schema(
            observation_request, is_viewer
        )

        versions_dictionary = await self._get_versions(
            observation_requests=[observation_request],
        )

        observation_request_schema.versions = [
            version
            for version in versions_dictionary.get(
                observation_request_schema.parent_id, []
            )
        ]

        return observation_request_schema

    async def get_many(
        self,
        params: schemas.ObservationRequestReadParams,
        auth_user: AuthUser | None,
    ) -> tuple[list[schemas.ObservationRequest], int]:
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
        list[tuple[models.ObservationRequest, int]]
            The list of ObservationRequest records and the total number of records
            as a tuple
        """
        observation_request_filter = self._get_filter(data=params)

        is_viewer_clause = ~(is_creator_clause(auth_user) | is_writer_clause(auth_user))

        if params.proposal_code or params.proposal_name or params.proposal_ids:
            observation_request_filter.append(
                or_(~is_viewer_clause, ~models.ObservationRequest.anonymize)
            )

        # subquery to allow for filtering on latest versions
        latest_observation_request_ids = (
            select(models.ObservationRequest.id)
            .filter(*observation_request_filter)
            .order_by(
                models.ObservationRequest.parent_id,
                models.ObservationRequest.created_on.desc(),
            )
            .distinct(models.ObservationRequest.parent_id)
            .subquery()
        )

        # query for latest versions and order them by created_on descending
        observation_request_query = (
            select(
                models.ObservationRequest,
                is_viewer_clause.label("is_viewer"),
            )
            .join(
                latest_observation_request_ids,
                models.ObservationRequest.id == latest_observation_request_ids.c.id,
            )
            .order_by(
                models.ObservationRequest.created_on.desc(),
            )
            .limit(params.page_limit)
            .offset(params.offset)
        )

        result = await self.db.execute(observation_request_query)
        observation_requests = result.tuples().all()

        # total_count query for pagination total result set info given filters
        count_query = select(
            func.count(distinct(models.ObservationRequest.parent_id))
        ).where(*observation_request_filter)
        total_count = (await self.db.execute(count_query)).scalar_one()

        versions_dictionary: dict[UUID, list[schemas.ObservationRequestVersion]] = {}

        if params.include_versions:
            versions_dictionary = await self._get_versions(
                [request for request, _ in observation_requests]
            )

        redacted_observation_requests: list[schemas.ObservationRequest] = []
        for observation_request, is_viewer in observation_requests:
            redacted_observation_request = self._redact_to_schema(
                observation_request, is_viewer
            )
            redacted_observation_request.versions = [
                version
                for version in versions_dictionary.get(
                    observation_request.parent_id, []
                )
            ]
            redacted_observation_requests.append(redacted_observation_request)

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
        await self._can_submit(
            [data.instrument_id]
        )  # Check if the instrument allows observation requests

        await self._assign_proposal_ids([data])
        observation_request = data.to_orm()
        observation_request.status = ObservationRequestStatus.PENDING.value
        observation_request.status_reason = "Awaiting review"
        observation_request.created_by_id = created_by_id

        self.db.add(observation_request)
        await self.db.commit()
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
        # Get list of instrument IDs from the requests to check if the submitter
        # can submit ToOs to all of them
        instrument_ids = [
            observation_request.instrument_id
            for observation_request in data.observation_requests
        ]

        await self._can_submit(
            instrument_ids
        )  # Check if the instruments allow observation requests

        await self._assign_proposal_ids(data.observation_requests)

        # Bulk add the ObservationRequest records to the database
        observation_request_records = []
        for observation_request_create in data.observation_requests:
            observation_request = observation_request_create.to_orm()
            observation_request.created_by_id = created_by_id
            observation_request.status = ObservationRequestStatus.PENDING.value
            observation_request.status_reason = "Awaiting review"

            observation_request_records.append(observation_request)

        self.db.add_all(observation_request_records)
        await self.db.commit()

        return [
            observation_request.id
            for observation_request in observation_request_records
        ]

    async def modify(
        self,
        observation_request_id: UUID,
        data: schemas.ObservationRequestUpdate,
        modified_by: AuthUser,
    ) -> UUID:
        """
        Modify an ObservationRequest given some changes.
        Upon modification, a new ObservationRequest is created with the changes,
        with the same parent_id as the original ObservationRequest.

        Parameters
        ----------
        observation_request_id: UUID
            the ID of the ObservationRequest to modify
        data : schemas.ObservationRequestUpdate
            the changes to the ObservationRequest
        modified_by: AuthUser
            the authenticated user making the request
        Returns
        -------
        models.ObservationRequest
            The ObservationRequest with the modifications
        """
        # pull existing version
        (observation_request, user_type) = await self._get_model(
            observation_request_id, modified_by
        )

        await self._can_modify(observation_request, data, user_type)

        # attempt to use the incoming instrument_id first with the assumption that instrument_id can be changed.
        instrument_id = data.instrument_id or observation_request.instrument_id
        await self._can_submit([instrument_id])

        # prevent overwriting stale edits
        await self._can_modify_version(observation_request)

        await self._assign_proposal_ids([data])

        # if changing to anonymize, update all versions to anonymize as well
        if (
            data.anonymize is not None
            and data.anonymize != observation_request.anonymize
        ):
            versions_query = select(models.ObservationRequest).where(
                models.ObservationRequest.parent_id == observation_request.parent_id
            )
            result = await self.db.execute(versions_query)
            versions = result.scalars().all()

            for version in versions:
                version.anonymize = data.anonymize

        # Keys that do not need to be copied over to the new version
        exclude_keys = [
            "id",
            "modified_by_id",
            "modified_on",
        ]

        # prepare data_to_modify dictionary with existing obsreq values
        db_keys = [
            column.name
            for column in observation_request.__table__.columns
            if column.name not in exclude_keys
        ]
        data_to_modify = {key: getattr(observation_request, key) for key in db_keys}

        # Include keys that are explicitly set by the user so explicit "None"s are preserved.
        # Override with None for keys explicitly set to None by the user.
        data_dict = data.model_dump(exclude_unset=True)

        # check what db keys are on the incoming data so the data to modify can be modified accordingly
        for db_key in db_keys:
            schema_key = data.get_schema_key(db_key)

            # Ensure the key exists before trying to copy it. This implies that the field
            # was explicitly set and if the value is None it is
            incoming_has_key = nested.has_key(data_dict, schema_key)

            if incoming_has_key:
                data_to_modify[db_key] = nested.get_value(data, schema_key)

        new_observation_request = models.ObservationRequest(**data_to_modify)
        new_observation_request.modified_by_id = modified_by.id
        new_observation_request.modified_on = datetime.datetime.now()

        self.db.add(new_observation_request)
        await self.db.commit()
        return new_observation_request.id

    async def _get_model(
        self, observation_request_id: UUID, auth_user: AuthUser | None = None
    ) -> tuple[models.ObservationRequest, UserType]:
        observation_request_exists_query = select(
            models.ObservationRequest,
            case(
                (is_writer_clause(auth_user), "writer"),
                (is_creator_clause(auth_user), "creator"),
                else_="viewer",
            ).label("user_type"),
        ).where(models.ObservationRequest.id == observation_request_id)

        exec = await self.db.execute(observation_request_exists_query)

        res = exec.one_or_none()

        if res is None:
            raise ObservationRequestNotFoundException(
                observation_request_id=observation_request_id
            )

        return res.tuple()

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

    async def _can_submit(self, instrument_ids: list[UUID]) -> None:
        """
        Check against instruments to ensure that they all have observation requests enabled.

        Parameters
        ----------
        instrument_ids : list[UUID]
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

    def _redact_to_schema(
        self, observation_request: models.ObservationRequest, is_viewer: bool
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
            schema.submitted_by = None
            schema.proposal = None
            schema.science_justification = ""

        return schema

    async def _get_versions(
        self,
        observation_requests: list[models.ObservationRequest],
    ) -> dict[UUID, list[schemas.ObservationRequestVersion]]:
        """
        Get the versions of the ObservationRequests.

        Parameters
        ----------
        observation_requests : list[tuple[models.ObservationRequest, bool]]
            The ObservationRequests to get the versions for
        is_viewer_clause: ColumnElement[bool] | False_
            The clause to determine if the user is a viewer

        Returns
        -------
        dict[UUID, list[schemas.ObservationRequestVersion]]
            A dictionary of parent_id to list of ObservationRequestVersion versions
        """
        related_request_dictionary: dict[
            UUID, list[schemas.ObservationRequestVersion]
        ] = {}

        if len(observation_requests) > 0:
            parent_ids = list(
                {
                    observation_request.parent_id
                    for observation_request in observation_requests
                }
            )

            related_request_query = (
                select(models.ObservationRequest)
                .where(models.ObservationRequest.parent_id.in_(parent_ids))
                .options(
                    load_only(
                        models.ObservationRequest.id,
                        models.ObservationRequest.created_on,
                        models.ObservationRequest.modified_on,
                        models.ObservationRequest.parent_id,
                    )
                )
            ).order_by(models.ObservationRequest.modified_on.desc().nulls_last())

            related_request_result = await self.db.execute(related_request_query)

            related_requests = related_request_result.scalars().all()

            for parent_id in parent_ids:
                related_request_dictionary[parent_id] = [
                    schemas.ObservationRequestVersion.from_orm(related_request)
                    for related_request in related_requests
                    if related_request.parent_id == parent_id
                ]

        return related_request_dictionary

    async def _can_modify_version(
        self, observation_request: models.ObservationRequest
    ) -> None:
        """
        Prevent overwriting stale edits by ensuring that the observation_request is
        the newest version from the list of all versions associated by parent_id

        Parameters
        ----------
        observation_request : models.ObservationRequest
            The ObservationRequest instance to check

        Returns
        -------
        None
            None if the ObservationRequest is modifiable, otherwise an exception is raised
        """
        versions_dictionary = await self._get_versions(
            observation_requests=[observation_request],
        )
        versions = versions_dictionary[observation_request.parent_id]
        newest_version: schemas.ObservationRequestVersion = versions[0]
        # prevent overwriting stale versions between multiple users by forcing modify to only allow when newest version
        if newest_version.id != observation_request.id:
            raise ObservationRequestConflictException(
                message=f"Cannot modify an ObservationRequest that has been modified. This could be because someone modified it as you were making your submission. Please verify existing data and then resubmit modify by specifying the newest version with id {newest_version.id!s}"
            )

    async def _assign_proposal_ids(
        self,
        requests: list[schemas.ObservationRequestCreate]
        | list[schemas.ObservationRequestUpdate],
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
            for observation_request in requests
            if observation_request.proposal is not None
        ]
        existing_proposal_records = await self._get_proposals(proposals)
        existing_proposals_dict = {
            proposal.name + proposal.code: proposal
            for proposal in existing_proposal_records
        }

        new_proposals: list[schemas.ObservingProposalCreate] = []

        for request_create in requests:
            if request_create.proposal is not None:
                proposal_name = request_create.proposal.name
                existing_proposal = existing_proposals_dict.get(
                    proposal_name + request_create.proposal.code, None
                )

                # set existing proposal to new obs_req, or create a new proposal
                if existing_proposal:
                    request_create.proposal.id = existing_proposal.id
                else:
                    new_proposal = schemas.ObservingProposalCreate(
                        **request_create.proposal.model_dump(),
                    )
                    new_proposal.id = uuid4()
                    new_proposals.append(new_proposal)
                    request_create.proposal.id = new_proposal.id

        await self._create_proposals(new_proposals)

    async def _get_proposals(
        self, proposals: list[schemas.ObservingProposalCreate]
    ) -> list[models.ObservingProposal]:
        names = [proposal.name for proposal in proposals]

        query = select(models.ObservingProposal).where(
            models.ObservingProposal.name.in_(names)
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

    async def _can_modify(
        self,
        observation_request: models.ObservationRequest,
        update_data: schemas.ObservationRequestUpdate,
        user_type: UserType,
    ) -> None:
        """
        Check if an ObservationRequest is modifiable.

        Parameters
        ----------
        observation_request : models.ObservationRequest
            The ObservationRequest instance to check
        user_type : UserType
            The type of user attempting to modify the ObservationRequest

        Returns
        -------
        None
            None if the ObservationRequest is modifiable, otherwise an exception is raised
        """
        # When there are a finite number of options for business state transitions,
        # consider using a rules matrix (similar to how the tests are setup) to
        # simplify these conditional checks.

        if user_type == "viewer":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        elif user_type == "creator":
            creator_locked_status = [
                ObservationRequestStatus.ARCHIVED.value,
                ObservationRequestStatus.REJECTED.value,
                ObservationRequestStatus.ACCEPTED.value,
            ]
            is_updating_locked = observation_request.status in creator_locked_status

            # creator can only update to pending, warning, archived
            writer_only_status = [
                ObservationRequestStatus.REJECTED.value,
                ObservationRequestStatus.ACCEPTED.value,
            ]
            is_updating_to_locked = update_data.status in writer_only_status

            if is_updating_locked:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Creator cannot modify an ObservationRequest that has been archived, rejected, or accepted.",
                )

            if is_updating_to_locked:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot modify the status or status reason of an ObservationRequest as a creator.",
                )

        # prevents duplicate records and prevents updates to records that should not be changed after
        # they have moved into a locked state without changing the status
        writer_locked_status = [
            ObservationRequestStatus.REJECTED.value,
            ObservationRequestStatus.ARCHIVED.value,
        ]
        if (
            observation_request.status == update_data.status
            and observation_request.status in writer_locked_status
        ):
            raise ObservationRequestConflictException(
                message="The ObservationRequest is locked, the status cannot be modified to same status."
            )
