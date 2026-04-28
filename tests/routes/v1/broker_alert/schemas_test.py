from across_server.db.models import (
    BrokerAlert as BrokerAlertModel,
)
from across_server.routes.v1.broker_alert.schemas import BrokerAlertCreate


class TestBrokerAlertCreateSchema:
    def test_to_orm_should_create_broker_alert(
        self, fake_broker_alert_create_schema: BrokerAlertCreate
    ) -> None:
        """Should create the broker alert record when successful"""
        broker_alert = fake_broker_alert_create_schema.to_orm()
        assert isinstance(broker_alert, BrokerAlertModel)
