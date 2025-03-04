from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import models
from ...db.database import get_session
from .exceptions import TelescopeNotFoundException


class TelescopeService:
    """
    Telescope service for managing astronomical Telescope records in the ACROSS SSA system.
    This service handles CRUD operations for Telescope records. This includes retrieval,
    and creation of new Telescope records in the database.

    Methods
    -------
    get(telescope_id: UUID) -> models.Telescope
        Retrieve the Telescope record with the given id.
    """

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get(self, telescope_id: UUID) -> models.Telescope:
        """
        Retrieve the Telescope record with the given id.

        Parameters
        ----------
        telescope_id : UUID
            the Telescope id

        Returns
        -------
        models.Telescope
            The Telescope with the given id

        Raises
        ------
        TelescopeNotFoundException
        """
        telescope = await self.db.get(models.Telescope, telescope_id)

        if telescope is None:
            raise TelescopeNotFoundException(telescope_id)

        return telescope
