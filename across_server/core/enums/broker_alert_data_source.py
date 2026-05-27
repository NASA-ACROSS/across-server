from enum import Enum


class BrokerAlertDataSource(str, Enum):
    TNS = "tns"
    BROKER = "broker"
    IGWN = "igwn"
    GCN = "gcn"
