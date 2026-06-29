from collections.abc import Sequence
from typing import Annotated, Any, Tuple
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, status
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import make_transient

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

    async def get(self, observation_request_id: UUID) -> models.ObservationRequest:
        """
        Retrieve the ObservationRequest record with the given id.

        Parameters
        ----------
        observation_request_id : UUID
            the ObservationRequest id
        Returns
        -------
        models.ObservationRequest
            The ObservationRequest with the given id
        Raises
        ------
        ObservationRequestNotFoundException
        """
        query = select(models.ObservationRequest).where(
            models.ObservationRequest.id == observation_request_id
        )

        result = await self.db.execute(query)
        observation_request = result.scalar_one_or_none()

        if observation_request is None:
            raise ObservationRequestNotFoundException(observation_request_id)

        return observation_request

    async def get_many(
        self, params: Any
    ) -> Sequence[Tuple[models.ObservationRequest, int]]:
        """
        Retrieve a list of ObservationRequest records
        based on the query parameters.

        Parameters
        ----------
        data : schemas.ObservationRequestReadParams
            class representing ObservationRequest filter parameters
        Returns
        -------
        Sequence[Tuple[models.ObservationRequest, int]]
            The list of ObservationRequest records and the total number of records
            as a tuple
        """
        observation_request_filter = self._get_filter(data=params)

        observation_request_query = (
            select(models.ObservationRequest, func.count().over().label("count"))
            .filter(*observation_request_filter)
            .order_by(models.ObservationRequest.created_on.desc())
            .limit(params.page_limit)
            .offset(params.offset)
        )

        result = await self.db.execute(observation_request_query)

        observation_requests = result.tuples().all()

        return observation_requests

    async def create(self, data: Any, auth_user: AuthUser) -> UUID:
        """
        Create a new ObservationRequest record in the database.

        Parameters
        -----------
        data : schemas.ObservationRequestCreate
            The ObservationRequest to be created.
        auth_user: AuthUser
            the user making the request
        Returns
        -------
        UUID:
            The id of the newly created ObservationRequest
        """
        observation_request = data.to_orm(created_by_id=auth_user.id)

        self.db.add(observation_request)
        await self.db.commit()

        return observation_request.id

    async def create_many(self, data: Any, auth_user: AuthUser) -> list[UUID]:
        """
        Create many new ObservationRequest records in the database.

        Parameters
        -----------
        data : schemas.ObservationRequestCreateMany
            The ObservationRequests to be created.
        auth_user: AuthUser
            the user making the request
        Returns
        -------
        list[UUID]:
            The ids of the newly created ObservationRequests
        """
        observation_requests = [
            observation_request.to_orm(created_by_id=auth_user.id)
            for observation_request in data
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

        # if the user doesn't have access to submit a ToO for one instrument but does for others,
        # we deny all create requests in the call
        if not all(
            instrument.is_observation_request_enabled for instrument in instruments
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        # Bulk add the ObservationRequest records to the database
        observation_requests_to_add = []
        for observation_request in observation_requests:
            observation_request.id = uuid4()
            observation_requests_to_add.append(observation_request)

        self.db.add_all(observation_requests_to_add)
        await self.db.commit()
        return [observation_request.id for observation_request in observation_requests]

    async def modify(self, data: Any, auth_user: AuthUser) -> models.ObservationRequest:
        """
        Modify an ObservationRequest given some changes.
        Upon modification, a new ObservationRequest is created with the changes,
        with the same parent_id as the original ObservationRequest.

        Parameters
        ----------
        data : ObservationRequestPut
            the changes to the ObservationRequest
        auth_user: AuthUser
            the user making the request
        Returns
        -------
        models.ObservationRequest
            The ObservationRequest with the modifications
        """
        query = select(models.ObservationRequest).where(
            models.ObservationRequest.id == data.id
        )
        result = await self.db.execute(query)
        observation_request = result.scalar_one_or_none()

        if observation_request is None:
            raise ObservationRequestNotFoundException(data.id)

        # Admins can modify all fields
        is_admin = False
        requested_group_id = (
            observation_request.instrument.telescope.observatory.group.id
        )
        for group in auth_user.groups:
            if requested_group_id == group.id and (
                group.is_admin or "group:observation:write" in group.scopes
            ):
                is_admin = True
                break

        if not is_admin:
            # If requester is not the request creator, raise 401 exception
            if observation_request.created_by_id != auth_user.id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            # Pop the fields that the user is not allowed to modify from the data object
            data.status = None
            data.status_reason = None

        # Pop the id so it isn't set
        data.id = None

        # Copy the existing observation request, change the values and commit
        self.db.expunge(observation_request)
        make_transient(observation_request)
        observation_request.id = uuid4()
        # Update the fields of the ObservationRequest with the new values
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(observation_request, field, value)

        self.db.add(observation_request)
        await self.db.commit()
        return observation_request

    async def delete(self, observation_request_id: UUID, auth_user: AuthUser) -> UUID:
        """
        Delete an ObservationRequest by ID.
        Instead of deleting the record, this method sets the status to "archived".

        Parameters
        ----------
        observation_request_id : UUID
            the ObservationRequest ID
        auth_user: AuthUser
            the user making the request
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

        if not self._is_admin_or_requester(observation_request, auth_user):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        observation_request.status = "archived"

        self.db.add(observation_request)
        await self.db.commit()

        return observation_request.id

    async def get_observation_request_history(
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

        return data_filter

    def _is_admin_or_requester(
        self, data: models.ObservationRequest, auth_user: AuthUser
    ) -> bool:
        """
        Check if the auth user is the submitter of the ObservationRequest or has write privileges
        for the observatory group that the requested instrument belongs to.

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
        if auth_user.id == data.created_by_id:
            return True

        requested_group_id = data.instrument.telescope.observatory.group.id
        for group in auth_user.groups:
            if requested_group_id == group.id and (
                group.is_admin or "group:observation:write" in group.scopes
            ):
                return True

        return False

    def _needs_redacting(
        self, data: models.ObservationRequest, auth_user: AuthUser
    ) -> bool:
        """
        Check if the ObservationRequest record needs to be redacted based on the request user.

        Parameters
        ----------
        data : models.ObservationRequest
            the ObservationRequest to redact
        auth_user: AuthUser
            the user making the request
        Returns
        -------
        bool
        """
        # If the user is the submitter, or has write privileges for the observatory group that the
        # requested instrument belongs to, does not require redacting
        if self._is_admin_or_requester(data, auth_user):
            return False

        return data.anonymize
