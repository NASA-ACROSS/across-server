from unittest.mock import AsyncMock

import pytest
from ratelimit.auths.jwt import EmptyInformation

import across_server.core.middleware.parse_client_ip as parse_client_ip_module
from across_server.core import config
from across_server.core.middleware.parse_client_ip import parse_client_ip

EXPECTED_FORWARDED_FOR_IP: str = "255.255.255.255"
EXPECTED_REAL_IP: str = "123.123.123.123"
FAKE_ALB_IP: str = "111.111.111.111"
FAKE_REV_PROXY_IP: str = "222.222.222.222"


@pytest.fixture(autouse=True)
def mock_client_ip(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock(return_value=(EXPECTED_REAL_IP, "8000"))

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
            (
                b"x-forwarded-for",
                f"{EXPECTED_FORWARDED_FOR_IP}".encode(),
            ),
        ],
    }


@pytest.fixture()
def fake_xff_depth(request: pytest.FixtureRequest) -> int:
    return getattr(request, "param", 0)


@pytest.fixture(autouse=True)
def mock_config(monkeypatch: pytest.MonkeyPatch, fake_xff_depth: int) -> None:
    monkeypatch.setattr(
        config,
        "XFF_DEPTH",
        fake_xff_depth,
    )


class TestParsingClientIpMiddleware:
    @pytest.mark.parametrize(
        "fake_xff_depth, ips",
        [
            (1, EXPECTED_FORWARDED_FOR_IP),
            (2, f"{EXPECTED_FORWARDED_FOR_IP},{FAKE_REV_PROXY_IP}"),
        ],
        # this pattern can be used to override fixture inputs
        indirect=["fake_xff_depth"],
    )
    @pytest.mark.asyncio
    async def test_should_output_xff_depth_forwarded_for_when_multiple_ips(
        self, fake_scope: dict, mock_client_ip: AsyncMock, ips: str
    ) -> None:
        mock_client_ip.side_effect = EmptyInformation(fake_scope)
        fake_scope["headers"] = [(b"x-forwarded-for", ips.encode())]

        ip = await parse_client_ip(fake_scope)

        assert ip == EXPECTED_FORWARDED_FOR_IP

    @pytest.mark.asyncio
    async def test_should_output_real_client_ip(self, fake_scope: dict) -> None:
        ip = await parse_client_ip(fake_scope)

        assert ip == EXPECTED_REAL_IP
