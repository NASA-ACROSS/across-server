from geoalchemy2 import WKTElement

from across_server.db.models import (
    Localization as LocalizationModel,
)
from across_server.db.models import (
    LocalizationContour as LocalizationContourModel,
)
from across_server.routes.v1.localization.schemas import (
    Localization,
    LocalizationContour,
    LocalizationCreate,
)


class TestLocalizationSchema:
    def test_from_orm_should_return_localization_for_point_source(
        self, fake_point_source_localization: LocalizationModel
    ) -> None:
        """Should return the localization schema when successful"""
        localization = Localization.from_orm(fake_point_source_localization)
        assert isinstance(localization, Localization)

    def test_from_orm_should_return_localization_for_nonlocalized_event(
        self, fake_localization_with_contour: LocalizationModel
    ) -> None:
        """Should return the localization schema when successful"""
        localization = Localization.from_orm(fake_localization_with_contour)
        assert isinstance(localization, Localization)


class TestLocalizationContourSchema:
    def test_from_orm_should_return_localization_contour(
        self, fake_localization_contour: LocalizationContourModel
    ) -> None:
        """Should return the localization contour schema when successful"""
        localization_contour = LocalizationContour.from_orm(fake_localization_contour)
        assert isinstance(localization_contour, LocalizationContour)

    def test_region_to_wkt_should_return_wktelement(
        self, fake_localization_contour_schema: LocalizationContour
    ) -> None:
        """Should return a WKTElement when converting shape"""
        element = fake_localization_contour_schema.region_to_wkt()
        assert isinstance(element, WKTElement)


class TestLocalizationCreateSchema:
    def test_to_orm_should_create_localization_for_point_source(
        self, fake_localization_create_schema: LocalizationCreate
    ) -> None:
        """Should create the localization schema when successful"""
        localization = fake_localization_create_schema.to_orm()
        assert isinstance(localization, LocalizationModel)

    def test_from_orm_should_return_localization_for_nonlocalized_event(
        self, fake_localization_create_schema_with_contours: LocalizationCreate
    ) -> None:
        """Should create the localization schema when successful"""
        localization = fake_localization_create_schema_with_contours.to_orm()
        assert isinstance(localization, LocalizationModel)
