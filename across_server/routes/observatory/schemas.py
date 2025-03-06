from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from ...core.schemas.base import BaseSchema, IDNameSchema
from ...db.models import Observatory as ObservatoryModel
from .enums import OBSERVATORY_TYPE


class ObservatoryBase(BaseSchema):
    """
    A Pydantic model class representing an Observatory in the ACROSS SSA system.

    Parameters
    ----------
    id : UUID
        Observatory id
    created_on : datetime
        Datetime the observatory was created in our database
    name : str
        Name of the observatory
    short_name : str
        Short Name of the observatory
    type: OBSERVATORY_TYPE
        Type of observatory (must be enum<GROUND_BASED, SPACE_BASED>)
    telescopes: list[IDNameSchema]
        List of telescopes belonging to observatory in id,name format
    """

    id: uuid.UUID
    created_on: datetime
    name: str
    short_name: str
    type: OBSERVATORY_TYPE
    telescopes: list[IDNameSchema]


class Observatory(ObservatoryBase):
    """
    A Pydantic model class representing a created observatory

    Notes
    -----
    Inherits from ObservatoryBase

    Methods
    -------
    from_orm(observatory: ObservatoryModel) -> Observatory
        Static method that instantiates this class from a observatory database record
    """

    @staticmethod
    def from_orm(observatory: ObservatoryModel) -> Observatory:
        """
        Method that converts a models.Observatory record to a schemas.Observatory
        Parameters
        ----------
        observatory: ObservatoryModel
            the models.Observatory record
        Returns
        -------
            schemas.Observatory
        """
        return Observatory(
            id=observatory.id,
            name=observatory.name,
            short_name=observatory.short_name,
            type=observatory.observatory_type,
            telescopes=[
                IDNameSchema(id=telescope.id, name=telescope.name)
                for telescope in observatory.telescopes
            ],
            created_on=observatory.created_on,
        )


class ObservatoryRead(BaseSchema):
    """
    A Pydantic model class representing the query parameters for the Observatory GET methods
    Parameters
    ----------
    name: Optional[str] = None
        Query Param for evaluating Observatory.name.contains(value)
    short_name: Optional[str] = None
        Query Param for evaluating Observatory.short_name.contains(value)
    type: Optional[OBSERVATORY_TYPE] = None
        Query Param for evaluating Observatory.type == value
    created_on: Optional[datetime] = None
        Query Param for evaluating Observatory.created_on > value
    """

    name: Optional[str] = None
    short_name: Optional[str] = None
    type: Optional[OBSERVATORY_TYPE]
    created_on: Optional[datetime] = None
