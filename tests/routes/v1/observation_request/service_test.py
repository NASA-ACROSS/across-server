from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from across_server.auth.schemas import AuthUser
from across_server.db import models
from across_server.routes.v1.observation_request import schemas
from across_server.routes.v1.observation_request.exceptions import (
    InvalidObservationRequestReadParametersException,
    ObservationRequestNotFoundException,
)
from across_server.routes.v1.observation_request.service import (
    ObservationRequestService,
)


class TestObservationRequestService:
    class TestGet:
        @pytest.mark.asyncio
        async def test_should_return_observation_request_when_found(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_observation_request: models.ObservationRequest,
        ) -> None:
            """Should return a schemas.ObservationRequest object"""
            mock_result.one_or_none.return_value = (fake_observation_request, True)
            mock_result.tuples.return_value.all.return_value = []

            service = ObservationRequestService(mock_db)
            observation_request = await service.get(uuid4(), auth_user=None)
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

    class TestGetMany:
        @pytest.mark.asyncio
        async def test_should_return_empty_list_when_nothing_matches_params(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            mock_observation_request_read_params: Any,
        ) -> None:
            """Should return empty list when nothing matches params"""
            mock_result.tuples.return_value.all.return_value = []

            service = ObservationRequestService(mock_db)
            values = await service.get_many(
                mock_observation_request_read_params, auth_user=None
            )
            assert len(values) == 0

        @pytest.mark.asyncio
        async def test_should_raise_422_with_bad_params(
            self,
            mock_db: AsyncMock,
            mock_observation_request_read_params: Any,
        ) -> None:
            """Should raise InvalidObservationRequestReadParametersException with bad params"""

            mock_observation_request_read_params.object_cone_search_ra = 123.45

            service = ObservationRequestService(mock_db)
            with pytest.raises(InvalidObservationRequestReadParametersException):
                await service.get_many(
                    mock_observation_request_read_params, auth_user=None
                )

    class TestCreate:
        @pytest.mark.asyncio
        async def test_should_save_observation_request_to_database(
            self,
            mock_db: AsyncMock,
            mock_observation_request_create: Any,
            fake_auth_user: AuthUser,
        ) -> None:
            """Should save the ObservationRequest to the database when successful"""
            service = ObservationRequestService(mock_db)
            await service.create(
                mock_observation_request_create,
                fake_auth_user.id,
            )

            mock_db.commit.assert_called_once()

    class TestCreateMany:
        @pytest.mark.asyncio
        async def test_should_commit_observation_requests_once(
            self,
            mock_db: AsyncMock,
            mock_result: MagicMock,
            mock_observation_request_create_many: Any,
            fake_auth_user: AuthUser,
        ) -> None:
            """Should save all ObservationRequests in one commit"""
            mock_result.scalars.return_value.all.return_value = []
            service = ObservationRequestService(mock_db)
            await service.create_many(
                mock_observation_request_create_many, fake_auth_user.id
            )

            mock_db.commit.assert_called_once()

        @pytest.mark.asyncio
        async def test_should_raise_error_if_instrument_observation_request_not_enabled(
            self,
            mock_db: AsyncMock,
            mock_result: MagicMock,
            mock_observation_request_create_many: Any,
            mock_instrument_data: models.Instrument,
            fake_auth_user: AuthUser,
        ) -> None:
            """Should raise an error if any instrument in the submitted requests does not have requests enabled"""
            mock_instrument_data.is_observation_request_enabled = False
            mock_result.scalars.return_value.all.return_value = [mock_instrument_data]
            service = ObservationRequestService(mock_db)
            with pytest.raises(HTTPException):
                await service.create_many(
                    mock_observation_request_create_many, fake_auth_user.id
                )

    class TestModify:
        @pytest.mark.asyncio
        async def test_should_raise_not_found_exception_when_does_not_exist(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_auth_user: AuthUser,
            mock_observation_request_create: Any,
        ) -> None:
            """Should raise ObservationRequestNotFoundException when the ObservationRequest does not exist"""
            mock_result.scalar_one_or_none.return_value = None

            service = ObservationRequestService(mock_db)
            with pytest.raises(ObservationRequestNotFoundException):
                await service.modify(
                    uuid4(), mock_observation_request_create, fake_auth_user.id
                )

        @pytest.mark.asyncio
        async def test_should_commit_changes_to_db(
            self,
            mock_db: AsyncMock,
            mock_result: AsyncMock,
            fake_auth_user: AuthUser,
            mock_observation_request_create: Any,
            fake_observation_request: models.ObservationRequest,
        ) -> None:
            """Should commit modifications of ObservationRequest to database"""
            mock_result.scalar_one_or_none.return_value = fake_observation_request

            service = ObservationRequestService(mock_db)

            await service.modify(
                uuid4(), mock_observation_request_create, fake_auth_user.id
            )
            mock_db.commit.assert_called_once()
