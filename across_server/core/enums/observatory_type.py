from enum import Enum


class ObservatoryType(str, Enum):
    SPACE_BASED = "SPACE_BASED"
    GROUND_BASED = "GROUND_BASED"

    @classmethod
    def get_args(cls) -> tuple[str, ...]:
        return tuple(x.value for x in cls)
