from enum import Enum


class EphemerisType(str, Enum):
    TLE = "tle"
    SPICE = "spice"
    JPL = "jpl"
    GROUND = "ground"
