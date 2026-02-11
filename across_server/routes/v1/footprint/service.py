from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import models
from ....db.database import get_session


class FootprintService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    async def get_from_instrument_ids(
        self, instrument_ids: list[UUID]
    ) -> Sequence[models.Footprint]:
        query = select(models.Footprint).where(
            models.Footprint.instrument_id.in_(instrument_ids)
        )

        result = await self.db.execute(query)
        footprints = result.scalars().all()

        return footprints
