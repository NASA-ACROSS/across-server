from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_session


class ObservationService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    # async def create(self, data: schemas.ObservationCreate) -> schemas.Observation:
    #     observation = data.to_orm()

    #     self.db.add(observation)
    #     await self.db.commit()
    #     await self.db.refresh(observation)

    #     return from_orm(data, observation)
