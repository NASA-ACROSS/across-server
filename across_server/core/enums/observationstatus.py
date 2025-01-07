from enum import Enum


class ObservationStatus(str, Enum):
    PLANNED = "planned"
    SCHEDULED = "scheduled"
    UNSCHEDULED = "unscheduled"
    PERFORMED = "performed"
    ABORTED = "aborted"
