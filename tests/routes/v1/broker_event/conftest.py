from collections.abc import Generator, Sequence
from datetime import datetime
from typing import Any, Tuple
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI

from across_server.core.enums import BrokerEventType
from across_server.db.models import (
    BrokerEvent as BrokerEventModel,
)
from across_server.routes.v1.broker_event.schemas import BrokerEventCreate
from across_server.routes.v1.broker_event.service import BrokerEventService


@pytest.fixture()
def fake_broker_event_create() -> BrokerEventCreate:
    return BrokerEventCreate(
        event_datetime=datetime.now(),
        type=BrokerEventType.TRANSIENT,
        name="test event",
    )


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
