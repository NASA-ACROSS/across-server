from enum import Enum


class ScheduleStatus(str, Enum):
    PLANNED = "planned"
    SCHEDULED = "scheduled"
    PERFORMED = "performed"
