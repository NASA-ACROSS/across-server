from across_server.db.models import BrokerEvent as BrokerEventModel
from across_server.routes.v1.broker_alert.schemas import BrokerAlert
from across_server.routes.v1.broker_event.schemas import BrokerEvent
from across_server.routes.v1.localization.schemas import Localization


class TestBrokerEventSchema:
    def test_from_orm_should_return_broker_event(
        self, fake_broker_event_data: BrokerEventModel
    ) -> None:
        """Should return the broker event schema when successful"""
        broker_event = BrokerEvent.from_orm(fake_broker_event_data)
        assert isinstance(broker_event, BrokerEvent)

    def test_from_orm_should_return_broker_alerts(
        self, fake_broker_event_data: BrokerEventModel
    ) -> None:
        """Should return broker alert schemas when successful"""
        broker_event = BrokerEvent.from_orm(fake_broker_event_data)
        assert all(
            [
                isinstance(broker_alert, BrokerAlert)
                for broker_alert in broker_event.broker_alerts
            ]
        )

    def test_from_orm_should_return_localizations(
        self, fake_broker_event_data: BrokerEventModel
    ) -> None:
        """Should return localization schemas when successful"""
        broker_event = BrokerEvent.from_orm(fake_broker_event_data)
        assert all(
            [
                isinstance(localization, Localization)
                for localization in broker_event.localizations
            ]
        )
