from pydantic import BaseModel, Field

from .base import PrefixMixin


class ProperMotion(BaseModel, PrefixMixin):
    """
    Proper motion describes the apparent motion of a celestial object across the sky.
    It is represented by right ascension (RA) and declination (Dec), along with an epoch,
    indicating the reference time for the measurements.
    """

    ra: float = Field()
    dec: float = Field()
    epoch: str = Field(max_length=16)
