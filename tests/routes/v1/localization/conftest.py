from uuid import uuid4

import pytest
from geoalchemy2 import WKTElement

from across_server.db.models import (
    Localization as LocalizationModel,
)
from across_server.db.models import (
    LocalizationContour as LocalizationContourModel,
)
from across_server.routes.v1.footprint.schemas import Point
from across_server.routes.v1.localization.schemas import (
    LocalizationContour,
    LocalizationCreate,
)


@pytest.fixture()
def fake_point_source_localization() -> LocalizationModel:
    return LocalizationModel(
        id=uuid4(),
        broker_alert_id=uuid4(),
        broker_event_id=uuid4(),
        ra=123.45,
        dec=-43.21,
    )


@pytest.fixture()
def fake_localization_contour() -> LocalizationContourModel:
    return LocalizationContourModel(
        id=uuid4(),
        contour=WKTElement(
            "POLYGON((123.0 -88.0, 124.0 -88.0, 124.0 -87.0, 123.0 -87.0, 123.0 -88.0))",
            srid=4326,
        ),
    )


@pytest.fixture()
def fake_localization_with_contour(
    fake_localization_contour: LocalizationContourModel,
) -> LocalizationModel:
    return LocalizationModel(
        id=uuid4(),
        broker_alert_id=uuid4(),
        broker_event_id=uuid4(),
        contours=[fake_localization_contour],
        probability_enclosed=0.5,
    )


@pytest.fixture()
def fake_localization_contour_schema() -> LocalizationContour:
    return LocalizationContour(
        id=uuid4(),
        contour=[
            Point(x=-0.5, y=-0.5),
            Point(x=-0.5, y=0.5),
            Point(x=0.5, y=0.5),
            Point(x=0.5, y=-0.5),
            Point(x=-0.5, y=-0.5),
        ],
    )


@pytest.fixture()
def fake_localization_create_schema() -> LocalizationCreate:
    return LocalizationCreate(ra=123.45, dec=-54.32)


@pytest.fixture()
def fake_localization_create_schema_with_contours(
    fake_localization_contour_schema: LocalizationContour,
) -> LocalizationCreate:
    return LocalizationCreate(
        probability_enclosed=0.5, contours=[fake_localization_contour_schema]
    )
