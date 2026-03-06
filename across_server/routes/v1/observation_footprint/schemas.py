from __future__ import annotations

import uuid

from geoalchemy2 import shape

from ....db.models import ObservationFootprint as ObservationFootprintModel
from ..footprint.schemas import FootprintBase, Point


class ObservationFootprintBase(FootprintBase):
    """
    A Pydantic model class representing an ObservationFootprint in the ACROSS SSA system.
    """


class ObservationFootprint(ObservationFootprintBase):
    """
    A Pydantic model class representing a created ObservationFootprint

    Notes
    -----
    Inherits from ObservationFootprintBase

    Methods
    -------
    from_orm(obj: ObservationFootprintModel) -> ObservationFootprint
        Static method that instantiates this class from an observation footprint database record
    """

    id: uuid.UUID
    observation_id: uuid.UUID

    @classmethod
    def from_orm(cls, obj: ObservationFootprintModel) -> ObservationFootprint:
        """
        Method that converts a models.ObservationFootprint record to a schemas.ObservationFootprint

        Parameters
        ----------
        obj: ObservationFootprintModel
            the models.ObservationFootprint record

        Returns
        -------
            schemas.ObservationFootprint
        """
        poly = shape.to_shape(obj.polygon)
        x, y = poly.exterior.coords.xy  # type: ignore
        polygon = [Point(x=x[i], y=y[i]) for i in range(len(x))]

        return cls(id=obj.id, observation_id=obj.observation_id, polygon=polygon)


class ObservationFootprintCreate(ObservationFootprintBase):
    """
    A Pydantic model class representing the data required to create an ObservationFootprint in the ACROSS SSA system.
    """

    def to_orm(self) -> ObservationFootprintModel:
        """
        Method that converts this class to an ORM representation for database insertion

        Returns
        -------
            ObservationFootprintModel
        """
        return ObservationFootprintModel(polygon=self.polygon_to_wkt())
