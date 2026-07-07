from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, Any, Tuple
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, status
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import make_transient, noload, selectinload

from ....auth.schemas import AuthUser
from ....core.constants import EARTH_CIRCUMFERENCE_METERS_PER_DEGREE
from ....db import models
from ....db.database import get_session
from .exceptions import (
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
    ) -> models.ObservationRequest:
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
        query_options = self._get_observation_request_query_options(
            include_history=True
        )
        query = (
            select(models.ObservationRequest)
            .where(models.ObservationRequest.id == observation_request_id)
            .options(query_options)  # type: ignore
        )

        result = await self.db.execute(query)
        observation_request = result.scalar_one_or_none()

        if observation_request is None:
            raise ObservationRequestNotFoundException(observation_request_id)

        observation_request = self._redact(observation_request, auth_user)

        return observation_request

    async def get_many(
        self,
        params: Any,
        auth_user: AuthUser,
    ) -> Sequence[Tuple[models.ObservationRequest, int]]:
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
        Sequence[Tuple[models.ObservationRequest, int]]
            The list of ObservationRequest records and the total number of records
            as a tuple
        """
        observation_request_filter = self._get_filter(data=params)

        query_options = self._get_observation_request_query_options(
            include_history=params.include_history
        )

        # TODO: Follow Kirill's PR for example
        observation_request_query = (
            select(models.ObservationRequest, func.count().over().label("count"))
            .filter(*observation_request_filter)
            .distinct(
                models.ObservationRequest.parent_id,
                models.ObservationRequest.created_on,
            )
            .order_by(
                models.ObservationRequest.created_on.desc(),
                models.ObservationRequest.parent_id,
            )
            .group_by(models.ObservationRequest.id)
            .limit(params.page_limit)
            .offset(params.offset)
            .options(query_options)  # type: ignore
        )

        result = await self.db.execute(observation_request_query)

        observation_requests = result.tuples().all()

        redacted_observation_requests: list[tuple[models.ObservationRequest, int]] = []
        for observation_request, count in observation_requests:
            redacted_observation_requests.append(
                (self._redact(observation_request, auth_user), count)
            )

        return redacted_observation_requests

    async def create(self, data: Any, created_by_id: UUID) -> UUID:
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
        query = select(models.ObservingProposal).where(
            models.ObservingProposal.name == data.proposal_name,
            models.ObservingProposal.code == data.proposal_code,
        )
        result = await self.db.execute(query)
        observing_proposal = result.scalar_one_or_none()

        if observing_proposal is None:
            new_observing_proposal = models.ObservingProposal(
                name=data.proposal_name, code=data.proposal_code
            )
            self.db.add(new_observing_proposal)
            await self.db.flush()
            proposal_id = new_observing_proposal.id
        else:
            proposal_id = observing_proposal.id

        observation_request = data.to_orm()
        observation_request.proposal_id = proposal_id
        observation_request.created_by_id = created_by_id

        self.db.add(observation_request)
        await self.db.commit()

        return observation_request.id

    async def create_many(self, data: Any, created_by_id: UUID) -> list[UUID]:
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
        observation_requests = [
            observation_request.to_orm() for observation_request in data
        ]

        # Get list of instrument IDs from the requests to check if the submitter
        # can submit ToOs to all of them
        instrument_ids = [
            observation_request.instrument_id
            for observation_request in observation_requests
        ]

        # Get the instruments from the database
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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        # Bulk add the ObservationRequest records to the database
        observation_request_records = []
        for observation_request in observation_requests:
            observation_request.created_by_id = created_by_id
            observation_request_records.append(observation_request)

        self.db.add_all(observation_request_records)
        await self.db.commit()
        return [observation_request.id for observation_request in observation_requests]

    async def modify(
        self, observation_request_id: UUID, data: Any, modified_by_id: UUID
    ) -> models.ObservationRequest:
        """
        Modify an ObservationRequest given some changes.
        Upon modification, a new ObservationRequest is created with the changes,
        with the same parent_id as the original ObservationRequest.

        Parameters
        ----------
        observation_request_id: UUID
            the ID of the ObservationRequest to modify
        data : ObservationRequestPut
            the changes to the ObservationRequest
        modified_by_id: UUID
            the ID of the user making the request
        Returns
        -------
        models.ObservationRequest
            The ObservationRequest with the modifications
        """
        # TODO: This should build the ORM model from the Pydantic model
        observation_request = data.to_orm()

        query = select(models.ObservationRequest).where(
            models.ObservationRequest.id == observation_request_id
        )
        result = await self.db.execute(query)
        observation_request = result.scalar_one_or_none()

        if observation_request is None:
            raise ObservationRequestNotFoundException(observation_request_id)

        # Copy the existing observation request, change the values and commit
        # Expunge removes the existing record from the session so it can be acted on
        # without changes affecting the existing record.
        self.db.expunge(observation_request)

        # allow sqlalchemy to use the existing record/model to create a new record
        make_transient(observation_request)

        # Generate a new id and created_on
        observation_request.id = uuid4()
        observation_request.created_on = datetime.now()
        # Update the fields of the ObservationRequest with the new values
        # TODO: Check if we can do this based on the final `ObservationRequestUpdate` schema
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(observation_request, field, value)

        self.db.add(observation_request)
        await self.db.commit()
        return observation_request

    async def update_status(
        self, observation_request_id: UUID, data: Any, modified_by_id: UUID
    ) -> UUID:
        """
        Delete an ObservationRequest by ID.
        Instead of deleting the record, this method sets the status to "archived".

        Parameters
        ----------
        observation_request_id : UUID
            the ObservationRequest ID
        data: schemas.ObservationRequestStatusUpdate
            the new status and reason for the ObservationRequest
        modified_by_id: UUID
            the UUID of the user deleting the ObservationRequest
        Returns
        -------
        UUID
            The ID of the deleted ObservationRequest
        """
        query = select(models.ObservationRequest).where(
            models.ObservationRequest.id == observation_request_id
        )
        result = await self.db.execute(query)
        observation_request = result.scalar_one_or_none()

        if observation_request is None:
            raise ObservationRequestNotFoundException(observation_request_id)

        # TODO: This shouldn't add a new record

        observation_request.status = data.status
        observation_request.status_reason = data.status_reason
        observation_request.modified_by_id = modified_by_id

        self.db.add(observation_request)
        await self.db.commit()

        return observation_request.id

    async def get_history(
        self, params: Any
    ) -> Sequence[Tuple[models.ObservationRequest, int]]:
        """
        Get all ObservationRequests associated with the given ObservationRequest ID.

        Parameters
        ----------
        params : ObservationRequestHistoryParams
            PaginationParams containing the ObservationRequest ID
        Returns
        -------
        Sequence[Tuple[models.ObservationRequest, int]]
            The list of ObservationRequest records and the total number of records
            as a tuple
        """
        query = select(models.ObservationRequest).where(
            models.ObservationRequest.id == params.observation_request_id
        )
        result = await self.db.execute(query)
        observation_request = result.scalar_one_or_none()

        if observation_request is None:
            raise ObservationRequestNotFoundException(params.observation_request_id)

        # TODO: Update this to follow Kirill's PR
        observation_request_history_query = (
            select(models.ObservationRequest, func.count().over().label("count"))
            .where(models.ObservationRequest.parent_id == observation_request.parent_id)
            .order_by(models.ObservationRequest.created_on.desc())
            .limit(params.page_limit)
            .offset(params.offset)
        )

        observation_request_history_result = await self.db.execute(
            observation_request_history_query
        )
        observation_requests = observation_request_history_result.tuples().all()

        # TODO: Redact
        return observation_requests

    def _get_filter(self, data: Any) -> list:
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
        data_filter = []

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
                            func.lower(models.Telescope.name).contains(
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

        # TODO: The proposal info needs to check auth user's permissions
        # to see the requests against the anonymize field.
        # Submitter + Admins can see all requests, but other users can only see non-anonymized requests
        # when filtering by proposal info
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

        # TODO: Filter on status as well?

        # TODO: Get history
        return data_filter

    def _is_requester(
        self, data: models.ObservationRequest, auth_user: AuthUser
    ) -> bool:
        """
        Check if the auth user is the submitter of the ObservationRequest.

        Parameters
        ----------
        data : models.ObservationRequest
            the ObservationRequest
        auth_user: AuthUser
            the user making the request
        Returns
        -------
        bool
        """
        return auth_user.id == data.created_by_id

    def _is_admin(self, data: models.ObservationRequest, auth_user: AuthUser) -> bool:
        """
        Check if the auth user has write privileges for the observatory group that the requested instrument belongs to.

        Parameters
        ----------
        data : models.ObservationRequest
            the ObservationRequest
        auth_user: AuthUser
            the user making the request
        Returns
        -------
        bool
        """
        requested_group_id = data.instrument.telescope.observatory.group.id
        for group in auth_user.groups:
            if requested_group_id == group.id and (
                group.is_admin
                or any(
                    scope in group.scopes
                    for scope in [
                        "group:observation_request:write",
                        "group:observation_request:read",
                    ]
                )
            ):
                return True

        return False

    def _get_observation_request_query_options(
        self, include_history: bool | None
    ) -> list[tuple]:
        if include_history:
            return selectinload(models.ObservationRequest.related_requests)  # type: ignore

        return noload(models.ObservationRequest.related_requests)  # type: ignore

    # TODO: Method to update status (and not create a new record)
    # This should replace the delete method

    # TODO: Should check "group:observation_request:write" and "group:observation_request:read"
    # in addition to is_admin. Check granular permissions for read vs write requests

    def _redact(
        self, observation_request: models.ObservationRequest, auth_user: AuthUser | None
    ) -> models.ObservationRequest:
        """
        Redact the ObservationRequest if the auth user is not the submitter or an admin.

        Parameters
        ----------
        observation_request : models.ObservationRequest
            the ObservationRequest to redact
        auth_user: AuthUser
            the user making the request
        Returns
        -------
        models.ObservationRequest
            The redacted ObservationRequest
        """
        is_admin = (
            self._is_admin(observation_request, auth_user)
            if auth_user is not None
            else False
        )
        is_requester = (
            self._is_requester(observation_request, auth_user)
            if auth_user is not None
            else False
        )

        if not is_admin and not is_requester:
            # Redact the fields that should not be visible to non-admins and non-submitters
            observation_request.created_by_id = None  # type: ignore
            observation_request.proposal_id = None  # type: ignore
            observation_request.observing_proposal = None  # type: ignore

        return observation_request
