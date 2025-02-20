from datetime import datetime
from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy import func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import models
from ...db.database import get_session
from . import schemas
from .exceptions import DuplicateTLEException


class TLEService:
    """
    Two-Line Element Set (TLE) service for managing satellite orbital data.
    This service handles CRUD operations for TLE data, including retrieval, existence checks,
    and creation of new TLE records in the database.

    Methods
    -------
    get(norad_id: int, epoch: datetime) -> Optional[models.TLE]
        Retrieve the TLE closest to the given epoch for a specific satellite.
    exists(norad_id: int, epoch: datetime) -> bool
        Check if a TLE exists for the given NORAD ID and epoch.
    create(data: schemas.TLECreate) -> models.TLE
        Create a new TLE record in the database.

    Attributes
    ----------
    db : AsyncSession
        The database session for executing queries.

    Notes
    -----
    The service uses SQLAlchemy for database operations and handles TLE data
    according to the standard TLE format specifications.
    """

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get(self, norad_id: int, epoch: datetime) -> Optional[models.TLE]:
        """
        Retrieves the closest TLE (Two-Line Element) entry for a given NORAD ID and epoch.

        Parameters
        ----------
        norad_id : int
            The NORAD catalog identifier for the satellite
        epoch : datetime
            The reference datetime to find the closest TLE entry

        Returns
        -------
        Optional[models.TLE]
            The closest TLE entry to the given epoch for the specified NORAD ID.
            Returns None if no entry is found.

        Notes
        -----
        The method orders results by the absolute difference between the TLE epoch
        and the provided epoch timestamp to find the closest match.
        """

        query = (
            select(models.TLE)
            .where(models.TLE.norad_id == norad_id)
            .order_by(
                func.abs(
                    func.extract("epoch", models.TLE.epoch)
                    - func.extract("epoch", literal(epoch))
                )
            )
        ).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def exists(
        self,
        norad_id: int,
        epoch: datetime,
    ) -> bool:
        """
        Check if a TLE exists in the database for a given norad_id and epoch.

        Parameters
        ----------
        norad_id : int
            NORAD catalog identifier for the satellite
        epoch : datetime
            Epoch timestamp of the TLE

        Returns
        -------
        bool
            True if TLE exists in database, False otherwise
        """
        # Query to check if TLE exists
        query = select(models.TLE).where(
            models.TLE.norad_id == norad_id, models.TLE.epoch == epoch
        )

        result = await self.db.execute(query)
        TLE = result.scalar_one_or_none()

        return bool(TLE)

    async def create(self, data: schemas.TLECreate) -> models.TLE:
        """
        Creates a new Two-Line Element (TLE) record in the database.
        Parameters
        ----------
        data : schemas.TLECreate
            The TLE data to be created, following the TLECreate schema format.

        Returns
        -------
        models.TLE
            The created TLE object with populated database fields.

        Raises
        ------
        DuplicateTLEException
            If a TLE with the same NORAD ID and epoch already exists in the database.

        Notes
        -----
        The function validates the input data, checks for duplicates based on NORAD ID
        and epoch, and performs the database insertion.
        """

        data_with_epoch = schemas.TLE.model_validate(data)

        exists = await self.exists(
            norad_id=data_with_epoch.norad_id, epoch=data_with_epoch.epoch
        )

        if exists:
            raise DuplicateTLEException(
                norad_id=data_with_epoch.norad_id, epoch=data_with_epoch.epoch
            )

        TLE = models.TLE(**data_with_epoch.model_dump(exclude_unset=True))

        self.db.add(TLE)
        await self.db.commit()
        await self.db.refresh(TLE)

        return TLE
