from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import models
from ...db.database import get_session
from . import schemas


class ObservationService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def create(self, data: schemas.ObservationCreate) -> schemas.Observation:
        orm_data = data.model_dump(flatten=True)
        observation = models.Observation(**orm_data)

        self.db.add(observation)
        await self.db.commit()
        await self.db.refresh(observation)

        return schemas.Observation.from_orm(observation)
