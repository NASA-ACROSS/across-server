import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Security, status

from .... import auth
from ....core.schemas import Page
from ..broker_event.schemas import BrokerEventCreate, BrokerEventReadParams
from ..broker_event.service import BrokerEventService
from ..localization.service import LocalizationService
from . import schemas
from .service import BrokerAlertService

router = APIRouter(
    prefix="/broker-alert",
    tags=["BrokerAlert"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The BrokerAlert does not exist.",
        },
    },
)


@router.get(
    "/{broker_alert_id}",
    summary="Read a broker alert",
    description="Read a broker alert by ID.",
    operation_id="get_broker_alert",
    status_code=status.HTTP_200_OK,
    response_model=schemas.BrokerAlert,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.BrokerAlert,
            "description": "Return a BrokerAlert",
        },
        status.HTTP_404_NOT_FOUND: {"description": "BrokerAlert not found"},
    },
)
async def get(
    service: Annotated[BrokerAlertService, Depends(BrokerAlertService)],
    broker_alert_id: uuid.UUID,
) -> schemas.BrokerAlert:
    broker_alert = await service.get(broker_alert_id)

    return schemas.BrokerAlert.model_validate(broker_alert)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Read broker alert(s)",
    description="Read many broker alerts based on query params",
    operation_id="get_broker_alerts",
    response_model=Page[schemas.BrokerAlert],
    responses={
        status.HTTP_200_OK: {
            "model": Page[schemas.BrokerAlert],
            "description": "Return broker alerts",
        },
    },
)
async def get_many(
    service: Annotated[BrokerAlertService, Depends(BrokerAlertService)],
    data: Annotated[schemas.BrokerAlertReadParams, Query()],
) -> Page[schemas.BrokerAlert]:
    broker_alert_tuples = await service.get_many(data)
    total_number = broker_alert_tuples[0][1] if broker_alert_tuples else 0
    broker_alerts = [tuple[0] for tuple in broker_alert_tuples]

    return Page[schemas.BrokerAlert].model_validate(
        {
            "total_number": total_number,
            "page": data.page,
            "page_limit": data.page_limit,
            "items": [
                schemas.BrokerAlert.model_validate(
                    broker_alert,
                )
                for broker_alert in broker_alerts
            ],
        }
    )


@router.post(
    "/",
    summary="Create a BrokerAlert",
    description="Create a new BrokerAlert and any new associated BrokerEvent or Localization records.",
    operation_id="create_broker_alert",
    status_code=status.HTTP_201_CREATED,
    response_model=uuid.UUID,
    responses={
        status.HTTP_201_CREATED: {
            "model": uuid.UUID,
            "description": "Created broker alert id",
        },
        status.HTTP_409_CONFLICT: {"description": "Duplicate broker alert"},
    },
    dependencies=[
        Security(auth.strategies.global_access, scopes=["system:broker-alert:write"])
    ],
)
async def create(
    broker_alert_service: Annotated[BrokerAlertService, Depends(BrokerAlertService)],
    broker_event_service: Annotated[BrokerEventService, Depends(BrokerEventService)],
    localization_service: Annotated[LocalizationService, Depends(LocalizationService)],
    data: schemas.BrokerAlertCreate,
) -> uuid.UUID:
    # Check for existing events
    broker_event_tuples = await broker_event_service.get_many(
        BrokerEventReadParams(
            type=[data.broker_event_type], name=data.broker_event_name
        )
    )
    total_number = broker_event_tuples[0][1] if broker_event_tuples else 0

    if total_number == 0:
        # Create the event and return the created model
        broker_event = await broker_event_service.create(
            BrokerEventCreate(
                event_datetime=data.broker_event_datetime,
                type=data.broker_event_type,
                name=data.broker_event_name,
            )
        )
    else:
        broker_event = broker_event_tuples[0][0]

    broker_alert = await broker_alert_service.create(
        data=data, broker_event=broker_event
    )

    if len(data.localizations):
        await localization_service.create_many(
            data.localizations, broker_event, broker_alert
        )

    return broker_alert.id
