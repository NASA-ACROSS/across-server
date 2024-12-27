from enum import Enum


class IVOAObsTrackingType(str, Enum):
    SIDEREAL = "sidereal"
    SOLAR_SYSTEM_OBJECT_TRACKING = "solar-system-object-tracking"
    FIXED_AZ_EL_TRANSIT = "fixed_az_el_transit"