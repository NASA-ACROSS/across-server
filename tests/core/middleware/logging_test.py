import pytest
import pytest_asyncio
import structlog
from httpx import AsyncClient

structlog.configure(cache_logger_on_first_use=False)


class TestLoggingMiddleware:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
    ) -> None:
        self.client = async_client
        self.endpoint = "/"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "key, expect_type", [("url", str), ("status_code", int), ("method", str)]
    )
    async def test_should_log_http_info(
        self, log_output: structlog.testing.LogCapture, key: str, expect_type: type
    ) -> None:
        """Should log request http data"""

        await self.client.get(self.endpoint)

        # call to the middleware logger will be the last/most recent
        log = log_output.entries[-1]

        assert isinstance(log["http"][key], expect_type)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("key, expect_type", [("ip", str), ("port", int)])
    async def test_should_log_network_info(
        self, log_output: structlog.testing.LogCapture, key: str, expect_type: type
    ) -> None:
        """Should log request network data"""

        await self.client.get(self.endpoint)

        # call to the middleware logger will be the last/most recent
        log = log_output.entries[-1]

        assert isinstance(log["network"]["client"][key], expect_type)

    @pytest.mark.asyncio
    async def test_should_log_duration(
        self, log_output: structlog.testing.LogCapture
    ) -> None:
        """Should log request duration in ns"""

        await self.client.get(self.endpoint)

        # call to the middleware logger will be the last/most recent
        log = log_output.entries[-1]

        assert isinstance(log["duration"], int)
