import pytest


@pytest.fixture(scope="session")
def version() -> str:
    return "v1"
