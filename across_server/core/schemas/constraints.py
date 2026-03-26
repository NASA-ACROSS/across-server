from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel

from across_server.core.enums.constraint_type import ConstraintType
from across_server.core.enums.solar_system_object import SolarSystemObject
from across_server.core.enums.twilight_type import TwilightType
from across_server.routes.v1.footprint.schemas import Footprint


class AirmassConstraint(BaseModel):
    short_name: Literal["Airmass"] = Field("Airmass", title="Short Name")
    name: ConstraintType = Field(ConstraintType.Airmass_Limit, title="Name")
    max_air_mass: float | None = Field(
        2.0,
        description="Maximum allowed airmass for observations",
        gt=1.0,
        title="Max Air Mass",
    )


class AltAzConstraint(BaseModel):
    short_name: str | None = Field("AltAz", title="Short Name")
    name: ConstraintType = Field(
        ConstraintType.Altitude_Azimuth_Avoidance, title="Name"
    )
    polygon: list[list[float]] | None = Field(None, title="Polygon")
    altitude_min: float | None = Field(None, ge=0.0, le=90.0, title="Altitude Min")
    altitude_max: float | None = Field(None, ge=0.0, le=90.0, title="Altitude Max")
    azimuth_min: float | None = Field(None, ge=0.0, lt=360.0, title="Azimuth Min")
    azimuth_max: float | None = Field(None, ge=0.0, lt=360.0, title="Azimuth Max")


class BrightStarConstraint(BaseModel):
    short_name: Literal["Bright Star"] = Field("Bright Star", title="Short Name")
    name: ConstraintType = Field(ConstraintType.Bright_Star_Avoidance, title="Name")
    min_separation: float | None = Field(
        5.0,
        description="Minimum angular separation (degrees) from bright stars",
        gt=0.0,
        title="Min Separation",
    )
    magnitude_limit: float | None = Field(
        6.0,
        description="Magnitude limit for stars to avoid (brighter than this)",
        title="Magnitude Limit",
    )


class ConstraintReason(BaseModel):
    start_reason: str = Field(..., title="Start Reason")
    end_reason: str = Field(..., title="End Reason")


# Logical constraints


class NotConstraint(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )
    name: ConstraintType = ConstraintType.Not


class OrConstraint(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )
    name: ConstraintType = ConstraintType.Or


class AndConstraint(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )
    name: ConstraintType = ConstraintType.And


class XorConstraint(BaseModel):
    model_config = ConfigDict(
        extra="allow",
    )
    name: ConstraintType = ConstraintType.Xor


# Astrophysical Constraints


class MoonAngleConstraint(BaseModel):
    short_name: Literal["Moon"] = Field("Moon", title="Short Name")
    name: ConstraintType = Field(ConstraintType.Moon_Angle, title="Name")
    min_angle: float | None = Field(
        None,
        description="Minimum angle from the Moon",
        ge=0.0,
        le=180.0,
        title="Min Angle",
    )
    max_angle: float | None = Field(
        None,
        description="Maximum angle from the Moon",
        ge=0.0,
        le=180.0,
        title="Max Angle",
    )


class SAAPolygonConstraint(BaseModel):
    short_name: str | None = Field("SAA", title="Short Name")
    name: ConstraintType = Field(ConstraintType.South_Atlantic_Anomaly, title="Name")
    polygon: list[list[float]] | None = Field(None, title="Polygon")


class SunAngleConstraint(BaseModel):
    short_name: Literal["Sun"] = Field("Sun", title="Short Name")
    name: ConstraintType = Field(ConstraintType.Sun_Angle, title="Name")
    min_angle: float | None = Field(
        None,
        description="Minimum angle from the Sun",
        ge=0.0,
        le=180.0,
        title="Min Angle",
    )
    max_angle: float | None = Field(
        None,
        description="Maximum angle from the Sun",
        ge=0.0,
        le=180.0,
        title="Max Angle",
    )


class DaytimeConstraint(BaseModel):
    short_name: Literal["Daytime"] = Field("Daytime", title="Short Name")
    name: ConstraintType = Field(ConstraintType.Daytime_Avoidance, title="Name")
    twilight_type: TwilightType | None = Field(
        TwilightType.astronomical,
        description="Type of twilight defining daytime boundaries",
    )


class Pointing(BaseModel):
    footprint: Footprint
    start_time: str | list[str] = Field(..., title="Start Time")
    end_time: str | list[str] = Field(..., title="End Time")


class PointingConstraint(BaseModel):
    short_name: Literal["Pointing"] = Field("Pointing", title="Short Name")
    name: ConstraintType = Field(ConstraintType.Pointing, title="Name")
    pointings: list[Pointing] = Field(..., title="Pointings")


class SolarSystemConstraint(BaseModel):
    short_name: Literal["Solar System"] = Field("Solar System", title="Short Name")
    name: ConstraintType = Field(
        ConstraintType.Solar_System_Object_Avoidance, title="Name"
    )
    min_separation: float | None = Field(
        10.0,
        description="Minimum angular separation (degrees) from Solar System objects",
        gt=0.0,
        title="Min Separation",
    )
    max_magnitude: float | None = Field(
        5.0,
        description="Maximum apparent magnitude of Solar System objects to consider",
        title="Max Magnitude",
    )
    bodies: list[SolarSystemObject | str] | None = Field(
        ["mercury", "venus", "mars", "jupiter", "saturn"],
        description="List of Solar System bodies to avoid",
        title="Bodies",
    )


class EarthLimbConstraint(BaseModel):
    short_name: Literal["Earth"] = Field("Earth", title="Short Name")
    name: ConstraintType = Field(ConstraintType.Earth_Limb, title="Name")
    min_angle: float | None = Field(
        None,
        description="Minimum angle from the Earth limb",
        ge=0.0,
        le=180.0,
        title="Min Angle",
    )
    max_angle: float | None = Field(
        None,
        description="Maximum angle from the Earth limb",
        ge=0.0,
        le=180.0,
        title="Max Angle",
    )


class GalacticBulgeConstraint(BaseModel):
    short_name: Literal["Galactic Bulge"] = Field("Galactic Bulge", title="Short Name")
    name: ConstraintType = Field(ConstraintType.Galactic_Bulge_Avoidance, title="Name")
    min_separation: float | None = Field(
        10.0,
        description="Minimum angular separation (degrees) from Galactic Bulge",
        gt=0.0,
        le=180.0,
        title="Min Separation",
    )


class GalacticPlaneConstraint(BaseModel):
    short_name: Literal["Galactic Plane"] = Field("Galactic Plane", title="Short Name")
    name: ConstraintType = Field(ConstraintType.Galactic_Plane_Avoidance, title="Name")
    min_latitude: float | None = Field(
        10.0,
        description="Minimum galactic latitude (degrees) for valid observations",
        ge=0.0,
        le=90.0,
        title="Min Latitude",
    )


class EclipticLatitudeConstraint(BaseModel):
    short_name: Literal["Ecliptic Latitude"] = Field(
        "Ecliptic Latitude", title="Short Name"
    )
    name: ConstraintType = Field(ConstraintType.Ecliptic_Latitude, title="Name")
    min_latitude: float | None = Field(
        15.0,
        description="Minimum ecliptic latitude (degrees) for valid observations",
        ge=0.0,
        le=90.0,
        title="Min Latitude",
    )


class Constraint(
    RootModel[
        EarthLimbConstraint
        | MoonAngleConstraint
        | SunAngleConstraint
        | SAAPolygonConstraint
        | AltAzConstraint
        | GalacticPlaneConstraint
        | BrightStarConstraint
        | AirmassConstraint
        | EclipticLatitudeConstraint
        | GalacticBulgeConstraint
        | SolarSystemConstraint
        | DaytimeConstraint
        | AndConstraint
        | OrConstraint
        | NotConstraint
        | XorConstraint
        | PointingConstraint
    ]
):
    root: (
        EarthLimbConstraint
        | MoonAngleConstraint
        | SunAngleConstraint
        | SAAPolygonConstraint
        | AltAzConstraint
        | GalacticPlaneConstraint
        | BrightStarConstraint
        | AirmassConstraint
        | EclipticLatitudeConstraint
        | GalacticBulgeConstraint
        | SolarSystemConstraint
        | DaytimeConstraint
        | AndConstraint
        | OrConstraint
        | NotConstraint
        | XorConstraint
        | PointingConstraint
    ) = Field(...)
