from enum import Enum


class ObservationStrategy(str, Enum):
    POINTED = "pointed"
    SURVEY = "survey"
