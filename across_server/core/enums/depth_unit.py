from enum import Enum


class DepthUnit(str, Enum):
    AB_MAG = "ab_mag"
    VEGA_MAG = "vega_mag"
    FLUX_ERG = "flux_erg"
    FLUX_JY = "flux_jy"

    def __str__(self) -> str:
        split_name = str(self.name).split("_")
        return str.upper(split_name[0]) + " " + split_name[1]
