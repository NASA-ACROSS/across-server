from .....core.schemas.base import BaseSchema


class NameResolverRead(BaseSchema):
    """
    Pydantic model class representing required parameters for
    the object name resolver GET method

    Parameters
    ----------
    name: str
        The name of the source to be resolved into coordinates.
    """

    object_name: str


class NameResolver(BaseSchema):
    """
    Pydantic model class representing a resolved object name

    Parameters
    ----------
    ra: float
        Right ascension coordinate, in degrees.
    dec: float
        Declination coordinate, in degrees.
    resolver: str
        Resolver used for resolving the coordinates.
    """

    ra: float
    dec: float
    resolver: str
