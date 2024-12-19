from sqlalchemy import Enum
from enum import Enum as TypeEnum


class PSQLTableEnum:
    @classmethod
    def table_name(cls):
        return cls.__name__

    @classmethod
    def to_psql_enum(cls, nullable=False) -> Enum:
        val = tuple([x.name for x in cls])
        e = Enum(*val, name=cls.table_name(), nullable=nullable)
        return e

class DepthUnit(str, PSQLTableEnum, TypeEnum):
    ab_mag = "ab_mag"
    vega_mag = "vega_mag"
    flux_erg = "flux_erg"
    flux_jy = "flux_jy"

    def table_name():  # type: ignore
        return "depth_unit"

    def __str__(self):
        split_name = str(self.name).split("_")
        return str.upper(split_name[0]) + " " + split_name[1]

class ObservationType(str, PSQLTableEnum, TypeEnum):
    imaging = "imaging"
    timing = "timing"
    spectroscopy = "spectroscopy"

    def table_name():  # type: ignore
        return "type"

class ObservationStatus(str, PSQLTableEnum, TypeEnum):
    planned = "planned"
    scheduled = "scheduled"
    unscheduled = "unscheduled"
    performed = "performed"
    aborted = "aborted"

    def table_name():  # type: ignore
        return "status"
    
class IVOAObsCategory(str, PSQLTableEnum, TypeEnum):
    fixed = "fixed"
    coordinated = "coordinated"
    window = "window"
    other = "other"

    def table_name():  # type: ignore
        return "category"

class IVOAObsTrackingType(str, PSQLTableEnum, TypeEnum):
    sidereal = "sidereal"
    solar_system_object_tracking = "solar-system-object-tracking"
    fixed_az_el_transit = "fixed_az_el_transit"

    def table_name():  # type: ignore
        return "tracking_type"