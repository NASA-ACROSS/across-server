import pytest
import structlog


@pytest.fixture(name="log_output")
def log_output():
    return structlog.testing.LogCapture()


@pytest.fixture(autouse=True)
def configure_structlog(log_output):
    structlog.configure(processors=[log_output])
