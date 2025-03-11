from __future__ import annotations

import uuid
from datetime import datetime

from ...core.enums import ObservatoryType
from ...core.schemas.base import BaseSchema, IDNameSchema
from ...db.models import Observatory as ObservatoryModel


class ObservatoryBase(BaseSchema):
    """
    A Pydantic model class representing an Observatory in the ACROSS SSA system.

    Parameters
    ----------
    id : UUID
        Observatory id
    created_on : datetime
        Datetime the observatory record was created
    name : str
        Name of the observatory
    short_name : str
        Short Name of the observatory
    type: ObservatoryType
        Type of observatory (must be enum<GROUND_BASED, SPACE_BASED>)
    telescopes: list[IDNameSchema]
        List of telescopes belonging to observatory in id,name format
    """

    id: uuid.UUID
    created_on: datetime
    name: str
    short_name: str
    type: ObservatoryType
    telescopes: list[IDNameSchema] | None = None


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
        Query param for evaluating Observatory.name.contains(value) or
        Observatory.short_name.contains(value)
    telescope_name: Optional[str] = None
        Query param for evaluating Observatory.telescopes.any((name or short_name).contains(value))
    telescope_id: Optional[UUID] = None
        Query param for evaluating Observatory.telescopes.any(id == value)
    type: Optional[ObservatoryType] = None
        Query param for evaluating Observatory.type == value
    created_on: Optional[datetime] = None
        Query param for evaluating Observatory.created_on > value
    """

    name: str | None = None
    type: ObservatoryType | None = None
    telescope_name: str | None = None
    telescope_id: uuid.UUID | None = None
    created_on: datetime | None = None
