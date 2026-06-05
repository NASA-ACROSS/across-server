from enum import Enum


class ObservationRequestStatus(str, Enum):
    ARCHIVED = "archived"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    PENDING = "pending"
    WARNING = "warning"
