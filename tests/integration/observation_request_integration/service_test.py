from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
import pytest_asyncio
from geoalchemy2.shape import from_shape
from pydantic import BaseModel
from shapely.geometry import Point

from across_server.auth.schemas import AuthUser
from across_server.core.schemas import PaginationParams
from across_server.db import database, models
from across_server.routes.v1.observation_request.service import (
    ObservationRequestService,
)

SEEDED_OBSERVATION_REQUEST_UUID = "6450ad6e-e185-4313-83b2-d6ed15bc11ca"

SEEDED_INSTRUMENT_UUID = "c31dc89c-d2f0-4335-9d6f-e42e7a7d86af"

SEEDED_TELESCOPE_UUID = "87e15f42-72c0-4973-a1f6-c23807cf90c5"

SEEDED_PROPOSAL_UUID = "3da50a07-39fd-4862-acc4-0e57bce144db"


class FakeObservationRequestCreate(BaseModel):
    instrument_id: UUID
    science_justification: str
    object_name: str
    object_ra: float
    object_dec: float
    object_position_error: float | None
    object_brightness: float
    object_brightness_unit: str
    date_range_begin: datetime
    date_range_end: datetime
    exposure_time: float
    anonymize: bool
    is_too: bool
    status: str
    instrument_configuration: dict | None

    def to_orm(self, created_by_id: UUID) -> models.ObservationRequest:
        return models.ObservationRequest(
            parent_id=UUID(SEEDED_OBSERVATION_REQUEST_UUID),
            object_position=from_shape(
                Point(self.object_ra, self.object_dec),  # type: ignore
                srid=4326,
            ),
            created_by_id=created_by_id,
            **self.model_dump(),
        )


class FakeObservationRequestModify(BaseModel):
    id: UUID
    instrument_configuration: dict | None = None
    status: str | None = None
    status_reason: str | None = None
    science_justification: str | None = None
    object_name: str | None = None
    object_ra: float | None = None
    object_dec: float | None = None
    object_position_error: float | None = None
    object_brightness: float | None = None
    object_brightness_unit: str | None = None
    date_range_begin: datetime | None = None
    date_range_end: datetime | None = None
    exposure_time: float | None = None
    anonymize: bool | None = None
    is_too: bool | None = None


class FakeObservationHistoryParams(PaginationParams):
    observation_request_id: UUID


class FakeObservationRequestReadParams(PaginationParams):
    telescope_names: list[str] | None = None
    telescope_ids: list[str] | None = None
    instrument_names: list[str] | None = None
    instrument_ids: list[str] | None = None
    object_name: str | None = None
    object_cone_search_ra: float | None = None
    object_cone_search_dec: float | None = None
    object_cone_search_radius: float | None = None
    begin_date: datetime | None = None
    end_date: datetime | None = None
    proposal_name: str | None = None
    proposal_code: str | None = None
    proposal_ids: list[str] | None = None
    is_too: bool | None = None
    parent_id: UUID | None = None


class TestObservationRequestService:
    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def setup(  # type: ignore
        self,
        mock_config_runtime_env_is_local: AsyncMock,
        mock_group_admin: AuthUser,
        mock_submitter: AuthUser,
    ):
        mock_config_runtime_env_is_local.return_value = True

        """Initialize DB and provide a session for each test."""
        database.init()

        self.group_admin = mock_group_admin
        self.submitter = mock_submitter
        self.observation_request_id = UUID(SEEDED_OBSERVATION_REQUEST_UUID)

        async with database.async_session() as session:
            self.session = session
            self.service = ObservationRequestService(session)
            yield
            await session.rollback()

    @pytest.mark.asyncio
    async def test_observation_request_get(self) -> None:
        """Should return the observation request with the given ID"""
        obs_request = await self.service.get(
            self.observation_request_id, self.submitter
        )

        assert obs_request.id == self.observation_request_id

    @pytest.mark.asyncio
    async def test_observation_request_create(self) -> None:
        """Should create observation request"""
        obs_request_create = FakeObservationRequestCreate(
            instrument_id=UUID(SEEDED_INSTRUMENT_UUID),
            science_justification="Test",
            object_name="Test Object",
            object_ra=123.45,
            object_dec=-76.54,
            object_position_error=0.1,
            object_brightness=12.34,
            object_brightness_unit="AB_mag",
            date_range_begin=datetime(2026, 6, 25),
            date_range_end=datetime(2026, 6, 26),
            exposure_time=3600.0,
            is_too=True,
            instrument_configuration={"mode": "timing"},
            anonymize=False,
            status="pending",
        )

        obs_request_id = await self.service.create(
            obs_request_create, self.submitter.id
        )
        assert isinstance(obs_request_id, UUID)

    @pytest.mark.asyncio
    async def test_observation_request_delete_admin(self) -> None:
        """Admins should be able to delete requests for their observatory group"""
        obs_request_id = await self.service.update_status(
            self.observation_request_id, self.group_admin.id
        )
        assert obs_request_id == self.observation_request_id
        obs_request = await self.service.get(obs_request_id, self.group_admin)
        assert obs_request.status == "archived"

    @pytest.mark.asyncio
    async def test_observation_request_modify_admin(self) -> None:
        """Admins should be able to modify requests for their observatory group"""
        obs_request_modify = FakeObservationRequestModify(
            id=self.observation_request_id,
            status="rejected",
            status_reason="I don't like this",
        )
        obs_request = await self.service.modify(obs_request_modify, self.group_admin)
        assert obs_request.status == "rejected"

    @pytest.mark.asyncio
    async def test_observation_request_modify_submitter(self) -> None:
        """Submitters should not be able to change the status of their observation requests"""
        # Create a new request
        obs_request_create = FakeObservationRequestCreate(
            instrument_id=UUID(SEEDED_INSTRUMENT_UUID),
            science_justification="I need this urgently to get a grant!",
            object_name="My new supernova",
            object_ra=43.21,
            object_dec=123.45,
            object_position_error=0.001,
            object_brightness=20.0,
            object_brightness_unit="AB_mag",
            date_range_begin=datetime(2026, 6, 29),
            date_range_end=datetime(2026, 6, 30),
            exposure_time=60.0,
            is_too=True,
            instrument_configuration={"mode": "imaging"},
            anonymize=True,
            status="pending",
        )
        submitted_obs_request_id = await self.service.create(
            obs_request_create, self.submitter.id
        )
        # Attempt to modify the status of the newly created request
        obs_request_modify = FakeObservationRequestModify(
            id=submitted_obs_request_id,
            status="accepted",
            status_reason="Let me in!",
        )
        obs_request = await self.service.modify(obs_request_modify, self.submitter.id)
        # Check that the submitter cannot change the status
        assert obs_request.status != "accepted"

    @pytest.mark.parametrize(
        "field, val",
        [
            ("object_name", "Test Object"),
            ("telescope_names", ["sand"]),
            ("telescope_ids", [SEEDED_TELESCOPE_UUID]),
            ("instrument_names", ["sand"]),
            ("instrument_ids", [SEEDED_INSTRUMENT_UUID]),
            ("begin_date", datetime(2026, 6, 25)),
            ("end_date", datetime(2026, 6, 26)),
            ("proposal_name", "Krusty Krab"),
            ("proposal_code", "12345"),
            ("proposal_ids", [SEEDED_PROPOSAL_UUID]),
            ("is_too", True),
        ],
    )
    @pytest.mark.asyncio
    async def test_observation_request_get_many(
        self,
        field: str,
        val: Any,
    ) -> None:
        """Should correctly filter on input filter params"""
        read_params = FakeObservationRequestReadParams(
            parent_id=self.observation_request_id, **{field: val}
        )

        obs_requests = await self.service.get_many(read_params, self.submitter)
        assert isinstance(obs_requests, list)
