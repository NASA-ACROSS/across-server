import pytest
import structlog


@pytest.fixture(name="log_output")
def log_output() -> structlog.testing.LogCapture:
    return structlog.testing.LogCapture()


@pytest.fixture(autouse=True)
def configure_structlog(log_output: structlog.testing.LogCapture) -> None:
    structlog.configure(processors=[log_output])
