from .....core.schemas.base import BaseSchema


class TOOToolkitPageConfigurationRead(BaseSchema):
    """
    Pydantic model class representing required parameters for
    the object name resolver GET method

    Parameters
    ----------
    instrument_id: str
        The ID of the instrument for which to retrieve the TOO toolkit page configuration.
    """

    instrument_id: str


class TOOToolkitPageConfiguration(BaseSchema):
    """
    Pydantic model class representing a resolved object name

    Parameters
    ----------
        configuration: dict
            A dictionary containing the TOO toolkit page configuration for the specified instrument.
    """

    configuration: dict
