from enum import Enum


class BrokerEventType(str, Enum):
    TRANSIENT = "transient"
    GW = "gw"
    NEUTRINO = "neutrino"
    GRB = "grb"
    FRB = "frb"
    XRT = "xrt"
