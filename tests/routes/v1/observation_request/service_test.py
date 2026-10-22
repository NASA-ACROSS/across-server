import uuid
from collections.abc import Callable
from datetime import timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from across_server.auth.schemas import AuthUser
from across_server.core.enums.observation_request_status import ObservationRequestStatus
from across_server.db import models
from across_server.routes.v1.observation_request import schemas
from across_server.routes.v1.observation_request.exceptions import (
    InvalidObservationRequestCreateParametersException,
    InvalidObservationRequestReadParametersException,
    ObservationRequestConflictException,
    ObservationRequestNotFoundException,
)
from across_server.routes.v1.observation_request.service import (
    ObservationRequestService,
    UserType,
)


@pytest.fixture()
def fake_user_type() -> UserType:
    return "viewer"


@pytest.fixture()
def fake_models_result(
    fake_observation_request_model: models.ObservationRequest,
    fake_user_type: UserType,
) -> list[tuple]:
    return [(fake_observation_request_model, fake_user_type)]


@pytest.fixture(autouse=True)
def mock_get_models_db_result(
    mock_result: AsyncMock,
    fake_models_result: list[tuple],
) -> None:
    mock_result.scalar_one.side_effect = lambda: len(fake_models_result)
    mock_result.tuples.return_value.all.side_effect = lambda: fake_models_result


class Setup:
    @pytest.fixture(autouse=True)
    def setup(self, mock_db: AsyncMock) -> None:
        self.service = ObservationRequestService(mock_db)


class TestObservationRequestService:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_observation_request_when_found(
            self,
        ) -> None:
            """Should return a schemas.ObservationRequest object"""
            observation_request = await self.service.get(uuid4(), auth_user=None)
            assert isinstance(observation_request, schemas.ObservationRequest)

        @pytest.mark.asyncio
        async def test_should_raise_not_found_exception_when_does_not_exist(
            self,
            fake_models_result: list[tuple],
        ) -> None:
            """Should raise ObservationRequestNotFoundException when the ObservationRequest does not exist"""
            fake_models_result.clear()

            with pytest.raises(ObservationRequestNotFoundException):
                await self.service.get(uuid4(), auth_user=None)

    class TestGetMany(Setup):
        @pytest.mark.asyncio
        async def test_should_return_empty_list_when_no_results(
            self,
            fake_models_result: list[tuple],
            fake_observation_request_read_params: Any,
        ) -> None:
            """Should return empty list when nothing matches params"""
            fake_models_result.clear()

            values, _ = await self.service.get_many(
                fake_observation_request_read_params, auth_user=None
            )
            assert len(values) == 0

        @pytest.mark.asyncio
        async def test_should_raise_422_with_bad_params(
            self,
            fake_observation_request_read_params: schemas.ObservationRequestReadParams,
        ) -> None:
            """Should raise InvalidObservationRequestReadParametersException with bad params"""
            fake_observation_request_read_params.object_cone_search_ra = 123.45

            with pytest.raises(InvalidObservationRequestReadParametersException):
                await self.service.get_many(
                    fake_observation_request_read_params,
                    auth_user=None,
                )

    class TestCreate(Setup):
        @pytest.mark.asyncio
        async def test_should_save_observation_request_to_database(
            self,
            mock_db: AsyncMock,
            fake_observation_request_create: schemas.ObservationRequestCreate,
            fake_auth_user: AuthUser,
        ) -> None:
            """Should save the ObservationRequest to the database when successful"""
            await self.service.create(
                fake_observation_request_create,
                fake_auth_user.id,
            )

            mock_db.commit.assert_called_once()

    class TestCreateMany(Setup):
        @pytest.mark.asyncio
        async def test_should_commit_observation_requests_once(
            self,
            mock_db: AsyncMock,
            mock_result: MagicMock,
            fake_observation_request_create_many: schemas.ObservationRequestCreateMany,
            fake_auth_user: AuthUser,
        ) -> None:
            """Should save all ObservationRequests in one commit"""
            mock_result.scalars.return_value.all.return_value = []
            await self.service.create_many(
                fake_observation_request_create_many, fake_auth_user.id
            )

            mock_db.commit.assert_called_once()

        @pytest.mark.asyncio
        async def test_should_raise_error_if_instrument_observation_request_not_enabled(
            self,
            mock_result: MagicMock,
            fake_observation_request_create_many: schemas.ObservationRequestCreateMany,
            mock_instrument_data: models.Instrument,
            fake_auth_user: AuthUser,
        ) -> None:
            """Should raise an error if any instrument in the submitted requests does not have requests enabled"""
            mock_instrument_data.is_observation_request_enabled = False
            mock_result.scalars.return_value.all.return_value = [mock_instrument_data]
            with pytest.raises(HTTPException):
                await self.service.create_many(
                    fake_observation_request_create_many, fake_auth_user.id
                )

    class TestModify(Setup):
        @pytest.fixture(autouse=True)
        def fake_user_type(self) -> UserType:
            return "creator"

        @pytest.fixture()
        def fake_proposal(
            self, fake_observation_request_data: dict
        ) -> schemas.ObservingProposal:
            return schemas.ObservingProposal(
                id=fake_observation_request_data["proposal"]["id"],
                code=fake_observation_request_data["proposal"]["code"],
                name=fake_observation_request_data["proposal"]["name"],
            )

        @pytest.fixture()
        def fake_observation_request_versions(
            self,
            fake_observation_request_model_factory: Callable[
                [], models.ObservationRequest
            ],
        ) -> list[models.ObservationRequest]:
            v1 = fake_observation_request_model_factory()

            return [v1]

        @pytest.fixture(autouse=True)
        def mock_scalars_all(
            self,
            mock_result: AsyncMock,
            mock_instrument_data: models.Instrument,
            fake_proposal: schemas.ObservingProposal,
            fake_observation_request_versions: list[models.ObservationRequest],
        ) -> None:
            mock_result.scalars.return_value.all.side_effect = [
                [mock_instrument_data],  # _can_submit: instruments query
                fake_observation_request_versions,  # _get_versions: versions query
                [fake_proposal],  # _get_proposals: proposals query
            ]

        @pytest.mark.asyncio
        async def test_should_raise_404_not_found_when_observation_request_does_not_exist(
            self,
            fake_models_result: list[tuple],
            fake_auth_user: AuthUser,
            fake_observation_request_update: schemas.ObservationRequestUpdate,
        ) -> None:
            """Should raise ObservationRequestNotFoundException when the observation request does not exist"""
            fake_models_result.clear()

            with pytest.raises(ObservationRequestNotFoundException) as exc_info:
                await self.service.modify(
                    uuid4(),
                    fake_observation_request_update,
                    fake_auth_user,
                )

            assert exc_info.value.status_code == 404

        @pytest.mark.parametrize(
            (
                "db_status",
                "user_type",
                "modified_status",
                "modified_status_reason",
                "expected_status_code",
            ),
            [
                (ObservationRequestStatus.PENDING.value, "viewer", None, None, 403),
                (
                    ObservationRequestStatus.REJECTED.value,
                    "creator",
                    ObservationRequestStatus.REJECTED.value,
                    None,
                    403,
                ),
                (ObservationRequestStatus.ARCHIVED.value, "creator", None, None, 403),
                (ObservationRequestStatus.REJECTED.value, "creator", None, None, 403),
                (ObservationRequestStatus.ACCEPTED.value, "creator", None, None, 403),
                (
                    ObservationRequestStatus.REJECTED.value,
                    "writer",
                    ObservationRequestStatus.REJECTED.value,
                    None,
                    409,
                ),
                (
                    ObservationRequestStatus.ARCHIVED.value,
                    "writer",
                    ObservationRequestStatus.ARCHIVED.value,
                    None,
                    409,
                ),
            ],
        )
        @pytest.mark.asyncio
        async def test_should_raise_http_exception_when_checking_can_modify(
            self,
            db_status: str,
            user_type: UserType,
            modified_status: ObservationRequestStatus,
            modified_status_reason: str,
            fake_auth_user: AuthUser,
            expected_status_code: int,
            fake_observation_request_model: models.ObservationRequest,
            fake_observation_request_update: schemas.ObservationRequestUpdate,
            fake_models_result: list[tuple],
        ) -> None:
            """Should raise ObservationRequestForbiddenException when a viewer tries modifying the observation request"""
            fake_observation_request_model.status = db_status

            fake_models_result.clear()
            fake_models_result.append((fake_observation_request_model, user_type))

            fake_observation_request_update.status = modified_status
            fake_observation_request_update.status_reason = modified_status_reason

            with pytest.raises(HTTPException) as exc_info:
                await self.service.modify(
                    uuid4(),
                    fake_observation_request_update,
                    fake_auth_user,
                )

            assert exc_info.value.status_code == expected_status_code

        @pytest.mark.asyncio
        async def test_should_raise_422_when_instrument_does_not_have_observation_request_enabled(
            self,
            fake_auth_user: AuthUser,
            mock_instrument_data: models.Instrument,
        ) -> None:
            mock_instrument_data.is_observation_request_enabled = False

            with pytest.raises(InvalidObservationRequestCreateParametersException):
                await self.service.modify(
                    uuid4(),
                    schemas.ObservationRequestUpdate(),
                    fake_auth_user,
                )

        @pytest.mark.asyncio
        async def test_should_successfully_modify_currently_accepted_when_user_type_is_writer(
            self,
            fake_auth_user: AuthUser,
            mock_db: AsyncMock,
            fake_observation_request_model_factory: Callable,
            fake_observation_request_update: schemas.ObservationRequestUpdate,
            fake_models_result: list[tuple[models.ObservationRequest, UserType]],
            fake_observation_request_versions: list[models.ObservationRequest],
        ) -> None:
            obs_req_model = fake_observation_request_model_factory()
            obs_req_model.status = ObservationRequestStatus.ACCEPTED.value
            fake_observation_request_update.status = ObservationRequestStatus.ACCEPTED

            fake_models_result.clear()
            fake_models_result.append((obs_req_model, "writer"))

            obs_req_version = fake_observation_request_model_factory()
            fake_observation_request_versions.clear()
            fake_observation_request_versions.append(obs_req_version)

            await self.service.modify(
                uuid4(),
                fake_observation_request_update,
                fake_auth_user,
            )

            mock_db.commit.assert_called_once()

        @pytest.mark.asyncio
        async def test_should_commit_changes_to_db(
            self,
            mock_db: AsyncMock,
            fake_auth_user: AuthUser,
            fake_observation_request_update: schemas.ObservationRequestUpdate,
        ) -> None:
            """Should commit modifications of ObservationRequest to database"""
            await self.service.modify(
                uuid4(),
                fake_observation_request_update,
                fake_auth_user,
            )
            mock_db.commit.assert_called_once()

        @pytest.mark.asyncio
        async def test_should_raise_409_when_modifying_stale_version(
            self,
            mock_result: AsyncMock,
            fake_auth_user: AuthUser,
            fake_observation_request_update: schemas.ObservationRequestUpdate,
            fake_observation_request_model_factory: Callable,
            mock_instrument_data: models.Instrument,
            fake_models_result: list[tuple],
        ) -> None:
            """Should raise 409 when modifying stale version"""
            # fake existing version
            fake_models_result.clear()
            fake_models_result.append(
                (fake_observation_request_model_factory(), "creator")
            )

            # default fixture fake_observation_request_update.id matches obs_req_version_one.id
            obs_req_version_one = fake_observation_request_model_factory()
            obs_req_version_two = fake_observation_request_model_factory()

            # simulate update against obs_req_version_one
            obs_req_version_two.id = uuid.uuid4()
            obs_req_version_two.modified_on = (
                obs_req_version_two.modified_on + timedelta(hours=10)
            )

            mock_result.scalars.return_value.all.side_effect = [
                [mock_instrument_data],  # _can_submit: instruments query
                [obs_req_version_two, obs_req_version_one],
                [],  # _get_proposals: no existing proposals
            ]
            with pytest.raises(ObservationRequestConflictException):
                await self.service.modify(
                    uuid4(),
                    fake_observation_request_update,
                    fake_auth_user,
                )
