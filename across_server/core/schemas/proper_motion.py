from pydantic import BaseModel, Field

from .base import PrefixMixin


class ProperMotion(BaseModel, PrefixMixin):
    """
    Proper motion describes the apparent motion of a celestial object across the sky.
    It is represented by right ascension (RA) and declination (Dec), along with an epoch,
    indicating the reference time for the measurements.
    """

    ra: float = Field(description="Component of proper motion in right ascension (RA).")
    dec: float = Field(description="Component of proper motion in declination (dec).")
    epoch: str = Field(
        max_length=16,
        description="Epoch of the proper motion measurement, e.g., 'J2000'.",
    )
