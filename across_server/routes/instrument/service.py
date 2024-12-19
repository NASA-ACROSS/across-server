from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from ...db import models
from ...db.database import get_session


class InstrumentService:

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)]
    ) -> None:
        self.db = db

    async def has_footprint(self, instrument_id: UUID) -> bool:
        query = select(models.Instrument).where(
            models.Instrument.id == instrument_id
        )

        result = await self.db.execute(query)
        instrument = result.scalar_one_or_none()

        if not instrument:
            return False

        return bool(instrument.footprints)