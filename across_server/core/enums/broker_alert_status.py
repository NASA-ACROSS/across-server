from enum import Enum


class BrokerAlertStatus(str, Enum):
    INITIAL = "initial"
    PRELIMINARY = "preliminary"
    CONFIRMED = "confirmed"
    RETRACTED = "retracted"
    EARLY_WARNING = "early_warning"
    CLASSIFIED = "classified"
