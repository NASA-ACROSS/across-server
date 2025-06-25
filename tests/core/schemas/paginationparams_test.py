import pytest

from across_server.core.schemas import PaginationParams


class TestPaginationParams:
    def test_offset_calculation(self, mock_pagination_data: dict) -> None:
        """Should calculate offset from page and page limit"""
        pagination_params = PaginationParams(**mock_pagination_data)
        assert pagination_params.offset is not None

    def test_should_throw_error_when_only_one_field_supplied(
        self, mock_pagination_data: dict
    ) -> None:
        """Should throw an error when only one of page and page limit are provided"""
        mock_pagination_data.pop("page")
        with pytest.raises(ValueError, match="Provide both"):
            PaginationParams(**mock_pagination_data)
