from collections.abc import Generator, Sequence
from datetime import datetime
from typing import Any, Tuple
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI

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
from across_server.routes.v1.broker_event.service import BrokerEventService


@pytest.fixture()
def fake_broker_event_data() -> BrokerEventModel:
    return BrokerEventModel(
        id=uuid4(),
        event_datetime=datetime.now(),
        type=BrokerEventType.TRANSIENT.value,
        name="SN2026test",
        broker_alerts=[
            BrokerAlertModel(
                id=uuid4(),
                payload={},
                checksum="",
                status=BrokerAlertStatus.INITIAL.value,
                broker_name="TNS",
                data_source=BrokerAlertDataSource.TNS.value,
                external_event_id="SN2026test",
                broker_event_id=uuid4(),
                broker_received_on=datetime.now(),
            )
        ],
        localizations=[
            LocalizationModel(
                id=uuid4(),
                broker_alert_id=uuid4(),
                broker_event_id=uuid4(),
                ra=123.45,
                dec=-43.21,
            )
        ],
    )


@pytest.fixture()
def fake_broker_event_many(
    fake_broker_event_data: BrokerEventModel,
) -> Sequence[Tuple[BrokerEventModel, int]]:
    return [
        (
            fake_broker_event_data,
            1,
        )
    ]


@pytest.fixture(scope="function")
def mock_broker_event_service(
    fake_broker_event_data: BrokerEventModel,
    fake_broker_event_many: Sequence[Tuple[BrokerEventModel, int]],
) -> Generator[AsyncMock]:
    mock = AsyncMock(BrokerEventService)

    mock.get = AsyncMock(return_value=fake_broker_event_data)
    mock.get_many = AsyncMock(return_value=fake_broker_event_many)

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI, fastapi_dep: Any, mock_broker_event_service: AsyncMock
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            BrokerEventService: lambda: mock_broker_event_service,
        }
    ):
        yield overrider
