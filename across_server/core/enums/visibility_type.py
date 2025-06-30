from enum import Enum


class VisibilityType(str, Enum):
    EPHEMERIS = "ephemeris"
    VO = "vo"
    CUSTOM = "custom"
