from enum import Enum


class ConstraintType(Enum):
    Sun_Angle = "Sun Angle"
    Moon_Angle = "Moon Angle"
    Earth_Limb = "Earth Limb"
    Window = "Window"
    Unknown = "Unknown"
    South_Atlantic_Anomaly = "South Atlantic Anomaly"
    Altitude_Azimuth_Avoidance = "Altitude/Azimuth Avoidance"
    Galactic_Plane_Avoidance = "Galactic Plane Avoidance"
    Bright_Star_Avoidance = "Bright Star Avoidance"
    Airmass_Limit = "Airmass Limit"
    Ecliptic_Latitude = "Ecliptic Latitude"
    Galactic_Bulge_Avoidance = "Galactic Bulge Avoidance"
    Solar_System_Object_Avoidance = "Solar System Object Avoidance"
    Daytime_Avoidance = "Daytime Avoidance"
    Test_Constraint = "Test Constraint"
    And = "And"
    Or = "Or"
    Not = "Not"
    Xor = "Xor"
    Pointing = "Pointing"
