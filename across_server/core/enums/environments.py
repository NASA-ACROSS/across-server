from enum import Enum


class Environments(Enum):
    LOCAL = "local"
    FEAT1 = "feat1"
    FEAT2 = "feat2"
    DEV = "dev"
    QA = "qa"
    STAGING = "staging"
    PRODUCTION = "prod"
