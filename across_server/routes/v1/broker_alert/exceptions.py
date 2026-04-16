import uuid

from fastapi import status

from ....core.exceptions import AcrossHTTPException, NotFoundException


class BrokerAlertNotFoundException(NotFoundException):
    def __init__(self, broker_alert_id: uuid.UUID):
        super().__init__(entity_name="BrokerAlert", entity_id=broker_alert_id)


class DuplicateBrokerAlertException(AcrossHTTPException):
    def __init__(self, broker_alert_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Duplicate BrokerAlert detected with id {broker_alert_id} already exists.",
            log_data={"entity": "BrokerAlert", "id": broker_alert_id},
        )
