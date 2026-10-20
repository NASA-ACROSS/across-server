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
    ObservationRequestNotFoundException,
)
from across_server.routes.v1.observation_request.service import (
    ObservationRequestService,
)


class Setup:
    @pytest.fixture(autouse=True)
    def setup(self, mock_db):
        self.service = ObservationRequestService(mock_db)


class TestObservationRequestService:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_observation_request_when_found(
            self,
            mock_result: AsyncMock,
            fake_observation_request_model: models.ObservationRequest,
        ) -> None:
            """Should return a schemas.ObservationRequest object"""
            mock_result.one_or_none.return_value = (
                fake_observation_request_model,
                True,
            )
            mock_result.tuples.return_value.all.return_value = []

            observation_request = await self.service.get(uuid4(), auth_user=None)
            assert isinstance(observation_request, schemas.ObservationRequest)

        @pytest.mark.asyncio
        async def test_should_raise_not_found_exception_when_does_not_exist(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
        ) -> None:
            """Should raise ObservationRequestNotFoundException when the ObservationRequest does not exist"""
            mock_result.one_or_none.return_value = None

            service = ObservationRequestService(mock_db)
            with pytest.raises(ObservationRequestNotFoundException):
                await service.get(uuid4(), auth_user=None)

    class TestGetMany(Setup):
        @pytest.mark.asyncio
        async def test_should_return_empty_list_when_nothing_matches_params(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_request_read_params: Any,
        ) -> None:
            """Should return empty list when nothing matches params"""
            mock_result.tuples.return_value.all.return_value = []
            mock_result.scalar_one.return_value = 0

            service = ObservationRequestService(mock_db)
            values, _ = await service.get_many(
                fake_observation_request_read_params, auth_user=None
            )
            assert len(values) == 0

        @pytest.mark.asyncio
        async def test_should_raise_422_with_bad_params(
            self,
            mock_db: AsyncMock,
            fake_observation_request_read_params: Any,
        ) -> None:
            """Should raise InvalidObservationRequestReadParametersException with bad params"""

            fake_observation_request_read_params.object_cone_search_ra = 123.45

            service = ObservationRequestService(mock_db)
            with pytest.raises(InvalidObservationRequestReadParametersException):
                await service.get_many(
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
            mock_db: AsyncMock,
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
        @pytest.mark.asyncio
        async def test_should_raise_404_not_found_when_observation_request_does_not_exist(
            self,
            mock_result: AsyncMock,
            fake_auth_user: AuthUser,
            fake_observation_request_update: schemas.ObservationRequestUpdate,
        ) -> None:
            """Should raise ObservationRequestNotFoundException when the observation request does not exist"""
            mock_result.one_or_none.return_value = None

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
                (ObservationRequestStatus.ARCHIVED.value, "creator", None, None, 409),
                (ObservationRequestStatus.REJECTED.value, "creator", None, None, 409),
                (ObservationRequestStatus.ACCEPTED.value, "creator", None, None, 409),
                (
                    ObservationRequestStatus.PENDING.value,
                    "creator",
                    ObservationRequestStatus.ARCHIVED,
                    None,
                    403,
                ),
                (
                    ObservationRequestStatus.WARNING.value,
                    "creator",
                    None,
                    "test status reason",
                    403,
                ),
            ],
        )
        @pytest.mark.asyncio
        async def test_should_raise_http_exception_when_checking_can_modify(
            self,
            mock_result: AsyncMock,
            db_status: str,
            user_type: str,
            modified_status: ObservationRequestStatus,
            modified_status_reason: str,
            fake_auth_user: AuthUser,
            expected_status_code: int,
            fake_observation_request_model: models.ObservationRequest,
            fake_observation_request_update: schemas.ObservationRequestUpdate,
        ) -> None:
            """Should raise ObservationRequestForbiddenException when a viewer tries modifying the observation request"""
            fake_observation_request_model.status = db_status
            mock_result.one_or_none.return_value = MagicMock(
                tuple=MagicMock(
                    side_effect=lambda: [fake_observation_request_model, user_type]
                )
            )

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
        async def test_should_raise_exception_when_instrument_does_not_have_observation_request_enabled(
            self,
            fake_auth_user: AuthUser,
            fake_observation_request_model: models.ObservationRequest,
            mock_instrument_data: models.Instrument,
            mock_result: AsyncMock,
        ):
            mock_instrument_data.is_observation_request_enabled = False
            mock_result.one_or_none.return_value = MagicMock(
                tuple=MagicMock(
                    side_effect=lambda: [fake_observation_request_model, "creator"]
                )
            )
            mock_result.scalar_one_or_none.side_effect = [
                fake_observation_request_model,
            ]
            mock_result.scalars.return_value.all.side_effect = [
                [mock_instrument_data],  # _can_submit: instruments query
                [],  # _get_proposals: no existing proposals
            ]
            with pytest.raises(InvalidObservationRequestCreateParametersException):
                await self.service.modify(
                    uuid4(),
                    schemas.ObservationRequestUpdate(),
                    fake_auth_user,
                )

        @pytest.mark.asyncio
        async def test_should_commit_changes_to_db(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_auth_user: AuthUser,
            fake_observation_request_update: schemas.ObservationRequestUpdate,
            fake_observation_request_model: models.ObservationRequest,
            mock_instrument_data: models.Instrument,
        ) -> None:
            """Should commit modifications of ObservationRequest to database"""
            mock_instrument_data.is_observation_request_enabled = True
            mock_result.one_or_none.return_value = MagicMock(
                tuple=MagicMock(
                    side_effect=lambda: [fake_observation_request_model, "creator"]
                )
            )
            mock_result.scalar_one_or_none.side_effect = [
                fake_observation_request_model,
            ]
            mock_result.scalars.return_value.all.side_effect = [
                [mock_instrument_data],  # _can_submit: instruments query
                [],  # _get_proposals: no existing proposals
            ]

            await self.service.modify(
                uuid4(),
                fake_observation_request_update,
                fake_auth_user,
            )
            mock_db.commit.assert_called_once()

    class TestArchive(Setup):
        @pytest.mark.asyncio
        async def test_should_set_status_to_archived(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_auth_user: AuthUser,
            fake_observation_request_model: models.ObservationRequest,
        ) -> None:
            """Should archive an ObservationRequest"""
            mock_result.one_or_none.return_value = MagicMock(
                tuple=MagicMock(
                    side_effect=lambda: [fake_observation_request_model, "creator"]
                )
            )

            await self.service.archive(
                uuid4(),
                fake_auth_user,
            )
            args = mock_db.add.call_args

            assert args[0][0].status == "archived"

        @pytest.mark.asyncio
        async def test_should_not_commit_to_db_when_already_archived(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_auth_user: AuthUser,
            fake_observation_request_model: models.ObservationRequest,
        ) -> None:
            fake_observation_request_model.status = "archived"
            mock_result.one_or_none.return_value = MagicMock(
                tuple=MagicMock(
                    side_effect=lambda: [fake_observation_request_model, "creator"]
                )
            )

            await self.service.archive(
                uuid4(),
                fake_auth_user,
            )
            mock_db.commit.assert_not_called()

        @pytest.mark.parametrize("status", ["accepted", "rejected"])
        @pytest.mark.asyncio
        async def test_should_raise_403_when_creator_tries_to_archive_when_status_cannot_be_archived(
            self,
            mock_result: AsyncMock,
            fake_auth_user: AuthUser,
            fake_observation_request_model: models.ObservationRequest,
            status: str,
        ) -> None:
            """Should raise 403 when creator tries to archive when status is not pending"""
            fake_observation_request_model.status = status
            mock_result.one_or_none.return_value = MagicMock(
                tuple=MagicMock(
                    side_effect=lambda: [fake_observation_request_model, "creator"]
                )
            )
            with pytest.raises(HTTPException) as exc_info:
                await self.service.archive(
                    uuid4(),
                    fake_auth_user,
                )

            assert exc_info.value.status_code == 403

        @pytest.mark.asyncio
        async def test_should_commit_to_db(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_auth_user: AuthUser,
            fake_observation_request_model: models.ObservationRequest,
        ) -> None:
            """Should archive an ObservationRequest"""
            mock_result.one_or_none.return_value = MagicMock(
                tuple=MagicMock(
                    side_effect=lambda: [fake_observation_request_model, "creator"]
                )
            )

            await self.service.archive(
                uuid4(),
                fake_auth_user,
            )

            mock_db.commit.assert_called_once()
