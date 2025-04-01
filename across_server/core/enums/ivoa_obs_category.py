from enum import Enum


class IVOAObsCategory(str, Enum):
    FIXED = "fixed"
    COORDINATED = "coordinated"
    WINDOW = "window"
    OTHER = "other"
