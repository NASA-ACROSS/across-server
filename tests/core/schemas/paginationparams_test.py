from across_server.core.schemas import PaginationParams


class TestPaginationParams:
    def test_offset_calculation(self, mock_pagination_data: dict) -> None:
        """Should calculate offset from page and page limit"""
        pagination_params = PaginationParams(**mock_pagination_data)
        assert pagination_params.offset is not None

    def test_should_set_defaults_for_page_and_page_limit(
        self,
    ) -> None:
        """Should set defaults for page and page_limit when non are supplied"""

        pagination_params = PaginationParams()
        assert pagination_params.page is not None
        assert pagination_params.page_limit is not None

    def test_should_set_page_when_only_page_limit_supplied(
        self, mock_pagination_data: dict
    ) -> None:
        """Should set page when only page_limit is supplied"""
        mock_pagination_data.pop("page")

        pagination_params = PaginationParams(**mock_pagination_data)
        assert pagination_params.page is not None

    def test_should_set_page_limit_when_only_page_supplied(
        self, mock_pagination_data: dict
    ) -> None:
        """Should set page_limit when only page is supplied"""
        mock_pagination_data.pop("page_limit")

        pagination_params = PaginationParams(**mock_pagination_data)
        assert pagination_params.page_limit is not None
