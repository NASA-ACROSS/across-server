from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field, computed_field


class TLEBase(BaseModel):
    """
    A Pydantic model class representing the base Two-Line Element Set (TLE) format.
    Parameters
    ----------
    norad_id : int
        NORAD Catalog Number/Satellite ID
    satellite_name : str
        Name of the satellite
    tle1 : str
        First line of the TLE format, must be exactly 69 characters
    tle2 : str
        Second line of the TLE format, must be exactly 69 characters
    Notes
    -----
    TLE is a data format encoding orbital elements of Earth-orbiting objects
    used by NORAD and NASA.
    """

    norad_id: int
    satellite_name: str
    tle1: str = Field(min_length=69, max_length=69)
    tle2: str = Field(min_length=69, max_length=69)


class TLECreate(TLEBase):
    pass


class TLE(TLEBase):
    @computed_field  # type: ignore[prop-decorator]
    @property
    def epoch(self) -> datetime:
        """
        Calculate the Epoch of the TLE file. See
        https://celestrak.org/columns/v04n03/#FAQ04 for more information on how
        the year / epoch encoding works.

        Returns
        -------
            The calculated epoch of the TLE.
        """
        # Extract year and days from TLE
        tleepoch = self.tle1.split()[3]
        tleyear = int(tleepoch[:2])
        days = float(tleepoch[2:]) - 1

        # Calculate epoch date
        year = 2000 + tleyear if tleyear < 57 else 1900 + tleyear
        return datetime(year, 1, 1) + timedelta(days=days)

    # https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances
    model_config = ConfigDict(from_attributes=True)
