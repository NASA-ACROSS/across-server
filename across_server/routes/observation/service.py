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
