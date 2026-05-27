from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import models
from ....db.database import get_session
from . import schemas


class LocalizationService:
    """
    Localization service for managing localizations in the ACROSS SSA system.
    This service handles creation of Localization objects for BrokerEvents and BrokerAlerts.

    Methods
    -------
    create_many(localizations: list[schemas.LocalizationCreate]) -> list[UUID]
        Create new Localization records
    """

    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    async def create_many(
        self,
        localizations: list[schemas.LocalizationCreate],
        broker_event: models.BrokerEvent,
        broker_alert: models.BrokerAlert,
    ) -> list[UUID]:
        """
        Create new Localization records in the database.

        Parameters
        -----------
        localizations : list[schemas.LocalizationCreate]
            The Localization data to be created.
        Returns
        -------
        list[uuid]:
            The UUIDs of the newly created Localization records
        """
        localization_ids = []
        for localization in localizations:
            localization_record = localization.to_orm()
            localization_record.id = uuid4()

            # Add localization to the event and alert
            localization_record.broker_alert_id = broker_alert.id
            localization_record.broker_event_id = broker_event.id
            self.db.add(localization_record)

            localization_ids.append(localization_record.id)

        await self.db.commit()
        return localization_ids
