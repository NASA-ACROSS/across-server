from datetime import datetime
from typing import Annotated, Tuple
from uuid import UUID

from fastapi import Depends
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import ColumnElement, False_, false, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

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


def _is_creator(
    auth_user: AuthUser | None,
) -> ColumnElement[bool] | False_:
    if auth_user is None:
        return false()
    return models.ObservationRequest.created_by_id == auth_user.id


def _is_admin(
    auth_user: AuthUser | None,
) -> ColumnElement[bool] | False_:
    if auth_user is None:
        return false()

    admin_group_ids = [
        group.id
        for group in auth_user.groups
        if getattr(group, "is_admin", False)
        or any(
            scope in getattr(group, "scopes", [])
            for scope in [
                "group:observation-request:write",
                "group:observation-request:read",
            ]
        )
    ]

    return models.ObservationRequest.instrument.has(
        models.Instrument.telescope.has(
            models.Telescope.observatory.has(
                models.Observatory.group.has(models.Group.id.in_(admin_group_ids))
            )
        )
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
        is_creator = _is_creator(auth_user)
        is_admin = _is_admin(auth_user)

        query = select(
            models.ObservationRequest,
            or_(is_creator, is_admin).label("is_admin_or_creator"),
        ).where(models.ObservationRequest.id == observation_request_id)

        result = await self.db.execute(query)
        (observation_request, is_admin_or_creator) = result.one_or_none() or (
            None,
            False,
        )

        if observation_request is None:
            raise ObservationRequestNotFoundException(observation_request_id)

        versions_query = (
            select(
                models.ObservationRequest,
                or_(is_creator, is_admin).label("is_admin_or_creator"),
            )
            .where(models.ObservationRequest.parent_id == observation_request.parent_id)
            .order_by(models.ObservationRequest.created_on.desc())
        )

        versions_result = await self.db.execute(versions_query)

        versions = versions_result.tuples().all()

        observation_request = schemas.ObservationRequest.from_orm(
            self._redact(observation_request, is_admin_or_creator)
        )

        observation_request.versions = [
            schemas.ObservationRequest.from_orm(
                self._redact(version, is_admin_or_creator)
            )
            for version, is_admin_or_creator in versions
            if version.id != observation_request.id
        ]

        return observation_request

    async def get_many(
        self,
        data: schemas.ObservationRequestReadParams,
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
        observation_request_filter = self._get_filter(data=data)
        is_creator = _is_creator(auth_user)
        is_admin = _is_admin(auth_user)
        is_admin_or_creator_query = or_(is_creator, is_admin)

        if data.proposal_code or data.proposal_name or data.proposal_ids:
            observation_request_filter.append(
                or_(is_admin_or_creator_query, ~models.ObservationRequest.anonymize)
            )

        observation_request_query = (
            select(
                models.ObservationRequest,
                is_admin_or_creator_query.label("is_admin_or_creator"),
            )
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
            .limit(data.page_limit)
            .offset(data.offset)
        )

        result = await self.db.execute(observation_request_query)
        observation_requests = result.tuples().all()

        # total_count query for pagination total result set info given filters
        count_query = (
            select(func.count())
            .select_from(models.ObservationRequest)
            .where(*observation_request_filter)
        )
        total_count = (await self.db.execute(count_query)).scalar_one()

        related_request_dictionary: dict[UUID, list[schemas.ObservationRequest]] = {}

        if data.include_versions:
            parent_ids = list(
                set(
                    [
                        observation_request.parent_id
                        for observation_request, _ in observation_requests
                    ]
                )
            )
            observation_ids = list(
                set(
                    [
                        observation_request.id
                        for observation_request, _ in observation_requests
                    ]
                )
            )

            related_request_query = (
                select(
                    models.ObservationRequest,
                    is_admin_or_creator_query.label("is_admin_or_creator"),
                ).where(
                    models.ObservationRequest.parent_id.in_(parent_ids),
                    ~models.ObservationRequest.id.in_(observation_ids),
                )
            ).order_by(models.ObservationRequest.created_on.desc())

            related_request_result = await self.db.execute(related_request_query)

            related_requests = related_request_result.tuples().all()

            for parent_id in parent_ids:
                related_request_dictionary[parent_id] = [
                    schemas.ObservationRequest.from_orm(
                        self._redact(related_request, is_admin_or_creator)
                    )
                    for related_request, is_admin_or_creator in related_requests
                    if related_request.parent_id == parent_id
                ]

        redacted_observation_requests: list[schemas.ObservationRequest] = []
        for observation_request, is_admin_or_creator in observation_requests:
            redacted_observation_request = schemas.ObservationRequest.from_orm(
                self._redact(observation_request, is_admin_or_creator)
            )
            redacted_observation_request.versions = (
                related_request_dictionary.get(observation_request.parent_id, [])
                if observation_request.parent_id in related_request_dictionary.keys()
                else []
            )
            redacted_observation_requests.append((redacted_observation_request))

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
        instrument_query = select(models.Instrument).where(
            models.Instrument.id == data.instrument_id
        )
        result = await self.db.execute(instrument_query)
        instrument = result.scalar_one_or_none()

        if instrument is None or not instrument.is_observation_request_enabled:
            raise InvalidObservationRequestCreateParametersException(
                message="The instrument does not allow observation requests."
            )

        # pull into a private method
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

        proposal_names = [
            observation_request.proposal_name
            for observation_request in data.observation_requests
        ]

        observing_proposal_query = select(models.ObservingProposal).where(
            models.ObservingProposal.name.in_(proposal_names)
        )
        observing_proposal_result = await self.db.execute(observing_proposal_query)
        observing_proposals = observing_proposal_result.scalars().all()

        observation_requests: list[models.ObservationRequest] = []
        for observation_request_create in data.observation_requests:
            observing_proposal = next(
                (
                    proposal
                    for proposal in observing_proposals
                    if proposal.name == observation_request_create.proposal_name
                ),
                None,
            )
            observation_request_model = observation_request_create.to_orm()
            if observing_proposal is None:
                new_observing_proposal = models.ObservingProposal(
                    name=observation_request_create.proposal_name,
                    code=observation_request_create.proposal_code,
                )
                self.db.add(new_observing_proposal)
                await self.db.flush()
                observation_request_model.proposal_id = new_observing_proposal.id
            else:
                observation_request_model.proposal_id = observing_proposal.id
            observation_requests.append(observation_request_model)

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
            raise InvalidObservationRequestCreateParametersException(
                message="One or more instruments do not allow observation requests."
            )

        # Bulk add the ObservationRequest records to the database
        observation_request_records = []
        for observation_request in observation_requests:
            observation_request.created_by_id = created_by_id
            observation_request_records.append(observation_request)

        self.db.add_all(observation_request_records)
        await self.db.commit()
        return [observation_request.id for observation_request in observation_requests]

    async def modify(
        self,
        observation_request_id: UUID,
        data: schemas.ObservationRequestUpdate,
        modified_by_id: UUID,
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
        modified_by_id: UUID
            the ID of the user making the request
        Returns
        -------
        models.ObservationRequest
            The ObservationRequest with the modifications
        """

        instrument_query = select(models.Instrument).where(
            models.Instrument.id == data.instrument_id
        )
        instrument_result = await self.db.execute(instrument_query)
        instrument = instrument_result.scalar_one_or_none()

        if instrument is None or not instrument.is_observation_request_enabled:
            raise InvalidObservationRequestCreateParametersException(
                message="The instrument does not allow observation requests."
            )

        proposal_query = select(models.ObservingProposal).where(
            models.ObservingProposal.name == data.proposal_name,
            models.ObservingProposal.code == data.proposal_code,
        )
        proposal_result = await self.db.execute(proposal_query)
        observing_proposal = proposal_result.scalar_one_or_none()

        if observing_proposal is None:
            new_observing_proposal = models.ObservingProposal(
                name=data.proposal_name, code=data.proposal_code
            )
            self.db.add(new_observing_proposal)
            await self.db.flush()
            proposal_id = new_observing_proposal.id
        else:
            proposal_id = observing_proposal.id

        observation_request_query = select(models.ObservationRequest).where(
            models.ObservationRequest.id == observation_request_id
        )
        observation_request_result = await self.db.execute(observation_request_query)
        observation_request = observation_request_result.scalar_one_or_none()

        if observation_request is None:
            raise ObservationRequestNotFoundException(observation_request_id)

        if data.anonymize != observation_request.anonymize:
            versions_query = select(models.ObservationRequest).where(
                models.ObservationRequest.parent_id == observation_request.parent_id
            )
            result = await self.db.execute(versions_query)
            versions = result.scalars().all()
            for version in versions:
                version.anonymize = data.anonymize

        data.parent_id = observation_request.parent_id or observation_request.id

        new_observation_request = data.to_orm()
        new_observation_request.created_by_id = observation_request.created_by_id
        new_observation_request.modified_by_id = modified_by_id
        new_observation_request.proposal_id = proposal_id
        new_observation_request.modified_on = datetime.now()
        new_observation_request.created_on = datetime.now()

        self.db.add(new_observation_request)
        await self.db.commit()
        return new_observation_request.id

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

    def _redact(
        self, observation_request: models.ObservationRequest, is_admin_or_creator: bool
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

        if observation_request.anonymize and not is_admin_or_creator:
            # Redact the fields that should not be visible to non-admins and non-submitters
            observation_request.created_by_id = None  # type: ignore
            observation_request.proposal_id = None  # type: ignore
            observation_request.observing_proposal = None  # type: ignore

        return observation_request
