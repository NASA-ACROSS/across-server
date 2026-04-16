import uuid

from geoalchemy2 import WKTElement, shape

from ....core.schemas.base import BaseSchema
from ....db.models import (
    Localization as LocalizationModel,
)
from ....db.models import (
    LocalizationContour as LocalizationContourModel,
)
from ..footprint.schemas import Point, Polygon


class LocalizationContourBase(BaseSchema):
    """
    A Pydantic model class representing a base LocalizationContour in the ACROSS system.

    Parameters
    ----------
    contour: list[Point]
        List of vertices mapping the localization region contours

    Methods
    ---------
    region_to_wkt:
        Convert the contour polygon to a WKT element
    """

    contour: list[Point]

    def region_to_wkt(self) -> WKTElement:
        """
        Method that converts the contour to a WKT Element

        Returns
        -------
            WKTElement: WKT representation of the regoion
        """
        points = [(point.x, point.y) for point in self.contour]

        shapely_polygon = Polygon(points)

        wkt_polygon = WKTElement(
            shapely_polygon.wkt,
            srid=4326,  # Specify the appropriate SRID
        )
        return wkt_polygon


class LocalizationContour(LocalizationContourBase):
    """
    A Pydantic model class representing a LocalizationContour in the ACROSS system.

    Parameters
    ----------
    id: UUID
        LocalizationContour UUID

    Methods
    ---------
    from_orm:
        Convert a models.LocalizationContour object to a schemas.LocalizationContour
    """

    id: uuid.UUID

    @classmethod
    def from_orm(cls, obj: LocalizationContourModel):  # type: ignore
        """
        Method that converts a models.LocalizationContour record to a schemas.LocalizationContour

        Parameters
        ----------
        obj: LocalizationContourModel
            the models.LocalizationContour record

        Returns
        -------
            schemas.LocalizationContour
        """
        poly = shape.to_shape(obj.contour)
        x, y = poly.exterior.coords.xy  # type: ignore
        contour = [Point(x=x[i], y=y[i]) for i in range(len(x))]

        return cls(id=obj.id, contour=contour)


class LocalizationBase(BaseSchema):
    """
    A Pydantic model class representing a base Localization in the ACROSS system.

    Parameters
    ----------
    ra : float, optional
        Right ascension of the localization, if it is a point source
    dec : float, optional
        Declination of the localization, if it is a point source
    contours: list[list[Point]], optional
        List of vertices mapping the localization region contours, if nonlocalized
    probability_enclosed: float, optional
        Probability enclosed by the contours, if nonlocalized

    Methods
    ---------
    region_to_wkt:
        Convert a geo object to a WKT element
    """

    ra: float | None = None
    dec: float | None = None
    contours: list[LocalizationContourBase] | None = None
    probability_enclosed: float | None = None


class Localization(LocalizationBase):
    """
    A Pydantic model class representing a Localization in the ACROSS system.
    Inherits from LocalizationBase

    Parameters
    ----------
    id : UUID
        Localization id
    broker_alert_id : UUID
        ID of the alert associated with this localization
    broker_event_id: UUID
        ID of the event associated with this localization
    """

    id: uuid.UUID
    broker_event_id: uuid.UUID
    broker_alert_id: uuid.UUID

    @classmethod
    def from_orm(cls, obj: LocalizationModel):  # type: ignore
        return cls(
            id=obj.id,
            broker_alert_id=obj.broker_alert_id,
            broker_event_id=obj.broker_event_id,
            ra=obj.ra,
            dec=obj.dec,
            contours=[LocalizationContour.from_orm(contour) for contour in obj.contours]
            if obj.contours is not None
            else None,
            probability_enclosed=obj.probability_enclosed,
        )


class LocalizationCreate(LocalizationBase):
    """
    A Pydantic model class representing data required to create a
    Localization object in the ACROSS system.
    Inherits from LocalizationBase

    Methods
    ----------
    to_orm:
        Returns an ORM Localization instance with the supplied data.
    """

    def to_orm(self) -> LocalizationModel:
        """
        Method that converts this class to an ORM representation for database insertion

        Returns
        -------
            LocalizationModel
        """
        return LocalizationModel(
            ra=self.ra,
            dec=self.dec,
            contours=[
                LocalizationContourModel(contour=contour.region_to_wkt())
                for contour in self.contours
            ]
            if self.contours is not None
            else [],
            probability_enclosed=self.probability_enclosed,
        )
