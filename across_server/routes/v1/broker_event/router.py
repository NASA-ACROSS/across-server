import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from ....core.schemas import Page
from . import schemas
from .service import BrokerEventService

router = APIRouter(
    prefix="/broker-event",
    tags=["BrokerEvent"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The BrokerEvent does not exist.",
        },
    },
)


@router.get(
    "/{broker_event_id}",
    summary="Read a broker event",
    description="Read a broker event by ID.",
    operation_id="get_broker_event",
    status_code=status.HTTP_200_OK,
    response_model=schemas.BrokerEvent,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.BrokerEvent,
            "description": "Return a BrokerEvent",
        },
        status.HTTP_404_NOT_FOUND: {"description": "BrokerEvent not found"},
    },
)
async def get(
    service: Annotated[BrokerEventService, Depends(BrokerEventService)],
    broker_event_id: uuid.UUID,
) -> schemas.BrokerEvent:
    broker_event = await service.get(broker_event_id)

    return schemas.BrokerEvent.from_orm(broker_event)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Read broker event(s)",
    description="Read many broker events based on query params",
    response_model=Page[schemas.BrokerEvent],
    responses={
        status.HTTP_200_OK: {
            "model": Page[schemas.BrokerEvent],
            "description": "Return broker events",
        },
    },
)
async def get_many(
    service: Annotated[BrokerEventService, Depends(BrokerEventService)],
    data: Annotated[schemas.BrokerEventReadParams, Query()],
) -> Page[schemas.BrokerEvent]:
    broker_event_tuples = await service.get_many(data)
    total_number = broker_event_tuples[0][1] if broker_event_tuples else 0
    broker_events = [tuple[0] for tuple in broker_event_tuples]

    return Page[schemas.BrokerEvent].model_validate(
        {
            "total_number": total_number,
            "page": data.page,
            "page_limit": data.page_limit,
            "items": [
                schemas.BrokerEvent.from_orm(
                    broker_event,
                )
                for broker_event in broker_events
            ],
        }
    )
