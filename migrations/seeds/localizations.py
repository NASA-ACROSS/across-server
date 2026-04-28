import uuid

from across_server.db.models import Localization, LocalizationContour

from .broker_alerts import sandy_alert
from .broker_events import sandy_event
from .footprints import create_polygon

vertices = [(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)]

localization_contour = LocalizationContour(
    id=uuid.UUID("436b1791-438b-4505-bde0-a3386e824c0f"),
    contour=create_polygon(vertices),
)

simple_localization = Localization(
    id=uuid.UUID("980ebcfa-4ef8-48a4-baaf-4cd859ed4546"),
    broker_alert_id=sandy_alert.id,
    broker_event_id=sandy_event.id,
    contours=[localization_contour],
    probability_enclosed=0.50,
)

localizations = [simple_localization]
