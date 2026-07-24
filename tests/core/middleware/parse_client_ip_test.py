from unittest.mock import AsyncMock

import pytest
from ratelimit.auths.jwt import EmptyInformation

import across_server.core.middleware.parse_client_ip as parse_client_ip_module
from across_server.core.middleware.parse_client_ip import parse_client_ip


@pytest.fixture(autouse=True)
def mock_client_ip(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock(return_value=("123.123.123.123", "8000"))

    monkeypatch.setattr(
        parse_client_ip_module,
        "client_ip",
        mock,
    )

    return mock


@pytest.fixture(autouse=True)
def fake_scope() -> dict:
    return {
        "type": "http",
        "headers": [
            (b"x-forwarded-for", b"255.255.255.255"),
        ],
    }


class TestParsingClientIpMiddleware:
    @pytest.mark.asyncio
    async def test_should_output_forwarded_for(
        self, fake_scope: dict, mock_client_ip: AsyncMock
    ) -> None:
        mock_client_ip.side_effect = EmptyInformation(fake_scope)

        ip = await parse_client_ip(fake_scope)

        assert ip == "255.255.255.255"

    @pytest.mark.asyncio
    async def test_should_output_last_forwarded_for_when_multiple_ips(
        self, fake_scope: dict, mock_client_ip: AsyncMock
    ) -> None:
        mock_client_ip.side_effect = EmptyInformation(fake_scope)
        fake_scope["headers"] = [
            (b"x-forwarded-for", b"111.111.111.111, 255.255.255.255"),
        ]

        ip = await parse_client_ip(fake_scope)

        assert ip == "255.255.255.255"

    @pytest.mark.asyncio
    async def test_should_output_real_client_ip(self, fake_scope: dict) -> None:
        ip = await parse_client_ip(fake_scope)

        assert ip == "123.123.123.123"
