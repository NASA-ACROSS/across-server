from across.tools import enums as tools_enums
from pydantic import BaseModel


class BandpassSearch(BaseModel):
    min: float
    max: float
    type: (
        tools_enums.WavelengthUnit | tools_enums.EnergyUnit | tools_enums.FrequencyUnit
    )
