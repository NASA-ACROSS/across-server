import uuid
from collections.abc import Callable, Generator
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

from across_server.auth.enums import PrincipalType
from across_server.auth.schemas import AuthUser, Group
from across_server.auth.strategies import (
    auth_user_or_none,
    authenticate_jwt,
    global_access,
)
from across_server.core.enums.observation_request_status import ObservationRequestStatus
from across_server.db import models
from across_server.routes.v1.observation_request.schemas import (
    ObservationRequest,
    ObservationRequestBase,
    ObservationRequestCreate,
    ObservationRequestCreateMany,
    ObservationRequestReadParams,
    ObservationRequestUpdate,
)
from across_server.routes.v1.observation_request.service import (
    ObservationRequestService,
)


@pytest.fixture(autouse=True)
def fake_observation_request_data(mock_instrument_data: models.Instrument) -> dict:
    return {
        "id": uuid.uuid4(),
        "science_justification": "test science justification",
        "object_name": "test object",
        "object_coordinates": {"ra": 123.1, "dec": 42.1},
        "object_position_error": 13.3,
        "object_brightness": {"value": 321.3, "unit": "ab_mag"},
        "observation_window": {
            "begin": datetime.now() + timedelta(days=3),
            "end": datetime.now() + timedelta(days=7),
        },
        "exposure_time": 3000,
        "anonymize": False,
        "is_too": True,
        "instrument_id": mock_instrument_data.id,
        "instrument_configuration": None,
        "proposal": {
            "name": "Test Proposal",
            "code": "12345",
            "id": uuid.uuid4(),
        },
    }


@pytest.fixture(autouse=True)
def fake_observation_request_base(
    fake_observation_request_data: dict,
) -> ObservationRequestBase:
    return ObservationRequestBase(**fake_observation_request_data)


@pytest.fixture(autouse=True)
def fake_observation_request_create(
    fake_observation_request_base: ObservationRequestBase,
) -> ObservationRequestCreate:
    return ObservationRequestCreate(**fake_observation_request_base.model_dump())


@pytest.fixture(autouse=True)
def fake_observation_request_update(
    fake_observation_request_base: ObservationRequestBase,
) -> ObservationRequestUpdate:
    return ObservationRequestUpdate(**fake_observation_request_base.model_dump())


@pytest.fixture(autouse=True)
def fake_auth_user(fake_group: models.Group) -> AuthUser:
    return AuthUser(
        id=uuid.uuid4(),
        groups=[Group(id=fake_group.id, scopes=["mock_scope"])],
        scopes=["mock_scope"],
        first_name="Mock",
        last_name="User",
        username="mockuser",
        type=PrincipalType.USER,
    )


@pytest.fixture(autouse=True)
def fake_submitted_by_user(fake_auth_user: AuthUser) -> models.User:
    return models.User(
        first_name=fake_auth_user.first_name,
        last_name=fake_auth_user.last_name,
    )


@pytest.fixture()
def fake_observation_request_model_factory(
    fake_observation_request_data: dict,
    fake_user: models.User,
) -> Callable[[], models.ObservationRequest]:
    id = fake_observation_request_data["id"]

    def factory() -> models.ObservationRequest:
        return models.ObservationRequest(
            id=id,
            parent_id=id,
            status=ObservationRequestStatus.PENDING,
            status_reason="testing",
            science_justification=fake_observation_request_data[
                "science_justification"
            ],
            date_range_begin=fake_observation_request_data["observation_window"][
                "begin"
            ],
            date_range_end=fake_observation_request_data["observation_window"]["end"],
            object_ra=fake_observation_request_data["object_coordinates"]["ra"],
            object_dec=fake_observation_request_data["object_coordinates"]["dec"],
            object_position_error=fake_observation_request_data[
                "object_position_error"
            ],
            object_name=fake_observation_request_data["object_name"],
            object_brightness=fake_observation_request_data["object_brightness"][
                "value"
            ],
            object_brightness_unit=fake_observation_request_data["object_brightness"][
                "unit"
            ],
            instrument_id=fake_observation_request_data["instrument_id"],
            instrument_configuration=fake_observation_request_data[
                "instrument_configuration"
            ],
            exposure_time=fake_observation_request_data["exposure_time"],
            anonymize=fake_observation_request_data["anonymize"],
            is_too=fake_observation_request_data["is_too"],
            proposal_id=fake_observation_request_data["proposal"]["id"],
            created_by_id=fake_user.id,
            modified_by_id=fake_user.id,
            submitted_by_user=fake_user,
            # submitted_by=f"{fake_user.first_name} {fake_user.last_name}",
            created_on=datetime.now(),
            modified_on=datetime.now(),
        )

    return factory


@pytest.fixture(autouse=True)
def fake_observation_request_model(
    fake_observation_request_model_factory: Callable,
) -> models.ObservationRequest:
    return fake_observation_request_model_factory()


@pytest.fixture(autouse=True)
def fake_observation_request_read_params() -> ObservationRequestReadParams:
    return ObservationRequestReadParams()


@pytest.fixture
def fake_observation_request_schema(
    fake_observation_request_model: models.ObservationRequest,
) -> ObservationRequest:
    return ObservationRequest.from_orm(fake_observation_request_model)


@pytest.fixture
def fake_observation_request_create_many(
    fake_observation_request_create: ObservationRequestCreate,
) -> ObservationRequestCreateMany:
    return ObservationRequestCreateMany(
        observation_requests=[fake_observation_request_create]
    )


@pytest.fixture
def mock_observation_request_service(
    fake_observation_request_schema: ObservationRequest,
) -> AsyncMock:
    mock = AsyncMock(ObservationRequestService)
    mock.get = AsyncMock(return_value=fake_observation_request_schema)
    mock.get_many = AsyncMock(return_value=([fake_observation_request_schema], 1))
    mock.create = AsyncMock(return_value=fake_observation_request_schema.id)
    mock.create_many = AsyncMock(return_value=[fake_observation_request_schema.id])
    mock.modify = AsyncMock(return_value=fake_observation_request_schema.id)
    mock.archive = AsyncMock(return_value=None)

    return mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: MagicMock,
    mock_global_access: AsyncMock,
    fake_auth_user_or_none: AuthUser,
    mock_observation_request_service: AsyncMock,
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            auth_user_or_none: lambda: fake_auth_user_or_none,
            authenticate_jwt: lambda: AsyncMock(),
            global_access: lambda: mock_global_access,
            ObservationRequestService: lambda: mock_observation_request_service,
        }
    ):
        yield overrider
