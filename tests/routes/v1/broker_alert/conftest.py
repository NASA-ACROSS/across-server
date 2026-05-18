from collections.abc import Generator, Sequence
from typing import Any, Tuple
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

from across_server.auth import strategies
from across_server.core.enums import (
    BrokerAlertDataSource,
    BrokerAlertStatus,
    BrokerEventType,
)
from across_server.db.models import (
    BrokerAlert as BrokerAlertModel,
)
from across_server.db.models import (
    BrokerEvent as BrokerEventModel,
)
from across_server.db.models import (
    Localization as LocalizationModel,
)
from across_server.routes.v1.broker_alert.schemas import BrokerAlertCreate
from across_server.routes.v1.broker_alert.service import BrokerAlertService
from across_server.routes.v1.broker_event.service import BrokerEventService
from across_server.routes.v1.localization.service import LocalizationService


@pytest.fixture()
def fake_broker_alert_many(
    fake_broker_alert_data: BrokerAlertModel,
) -> Sequence[Tuple[BrokerAlertModel, int]]:
    return [
        (
            fake_broker_alert_data,
            1,
        )
    ]


@pytest.fixture()
def fake_broker_alert_post_data() -> dict:
    return {
        "payload": {},
        "status": BrokerAlertStatus.INITIAL.value,
        "broker_name": "TNS",
        "data_source": BrokerAlertDataSource.TNS.value,
        "broker_event_datetime": "2026-04-15T00:00:00",
        "broker_received_on": "2026-04-15T00:00:00",
        "broker_event_type": BrokerEventType.TRANSIENT.value,
        "broker_event_name": "SN2026test",
        "localizations": [
            {
                "ra": 123.45,
                "dec": -43.21,
            }
        ],
    }


@pytest.fixture()
def fake_broker_alert_create_schema(
    fake_broker_alert_post_data: dict,
) -> BrokerAlertCreate:
    return BrokerAlertCreate.model_validate(fake_broker_alert_post_data)


@pytest.fixture(scope="function")
def mock_broker_alert_service(
    fake_broker_alert_data: BrokerAlertModel,
    fake_broker_alert_many: Sequence[Tuple[BrokerAlertModel, int]],
) -> Generator[AsyncMock]:
    mock = AsyncMock(BrokerAlertService)

    mock.get = AsyncMock(return_value=fake_broker_alert_data)
    mock.get_many = AsyncMock(return_value=fake_broker_alert_many)
    mock.create = AsyncMock(return_value=fake_broker_alert_data)

    yield mock


@pytest.fixture(scope="function")
def mock_broker_event_service(
    fake_broker_event_data: BrokerEventModel,
    fake_broker_event_many: Sequence[Tuple[BrokerEventModel, int]],
) -> Generator[AsyncMock]:
    mock = AsyncMock(BrokerEventService)

    mock.get = AsyncMock(return_value=fake_broker_event_data)
    mock.get_many = AsyncMock(return_value=fake_broker_event_many)
    mock.create = AsyncMock(return_value=fake_broker_event_data)

    yield mock


@pytest.fixture(scope="function")
def mock_localization_service(
    fake_point_source_localization: LocalizationModel,
) -> Generator[AsyncMock]:
    mock = AsyncMock(LocalizationService)

    mock.create_many = AsyncMock(return_value=[fake_point_source_localization])

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: Any,
    mock_broker_alert_service: AsyncMock,
    mock_broker_event_service: AsyncMock,
    mock_localization_service: AsyncMock,
    mock_global_access: MagicMock,
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            BrokerAlertService: lambda: mock_broker_alert_service,
            BrokerEventService: lambda: mock_broker_event_service,
            LocalizationService: lambda: mock_localization_service,
            strategies.global_access: lambda: mock_global_access,
        }
    ):
        yield overrider


@pytest.fixture(
    params=[
        "status",
        "broker_name",
        "data_source",
        "broker_received_on",
        "payload",
        "broker_event_datetime",
        "broker_event_type",
        "broker_event_name",
        "localizations",
    ]
)
def required_fields(request: pytest.FixtureRequest) -> Any:
    """
    Parameters pop in the create routine to trigger 422
    """
    return request.param
