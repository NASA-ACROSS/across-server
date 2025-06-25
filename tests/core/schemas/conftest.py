import pytest


@pytest.fixture
def mock_pagination_data() -> dict:
    return {"page": 3, "page_limit": 10}
