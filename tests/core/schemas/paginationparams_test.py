from across_server.core.config import config
from across_server.core.schemas import PaginationParams


class TestPaginationParams:
    def test_offset_calculation(self, mock_pagination_data: dict) -> None:
        """Should calculate offset from page and page limit"""
        pagination_params = PaginationParams(**mock_pagination_data)
        assert pagination_params.offset is not None

    def test_should_set_default_for_page(
        self,
    ) -> None:
        """Should set default for page when none"""

        pagination_params = PaginationParams()
        assert pagination_params.page == 1

    def test_should_set_default_for_page_limit_from_config(
        self,
    ) -> None:
        """Should set default for page_limit when none"""

        pagination_params = PaginationParams()
        assert pagination_params.page_limit == config.DEFAULT_PAGE_LIMIT

    def test_should_default_page_to_one_when_only_page_limit_supplied(
        self, mock_pagination_data: dict
    ) -> None:
        """Should set page when only page_limit is supplied"""
        mock_pagination_data.pop("page")

        pagination_params = PaginationParams(**mock_pagination_data)
        assert pagination_params.page == 1

    def test_should_default_page_limit_from_config_when_only_page_supplied(
        self, mock_pagination_data: dict
    ) -> None:
        """Should set page_limit when only page is supplied"""
        mock_pagination_data.pop("page_limit")

        pagination_params = PaginationParams(**mock_pagination_data)
        assert pagination_params.page_limit == config.DEFAULT_PAGE_LIMIT
