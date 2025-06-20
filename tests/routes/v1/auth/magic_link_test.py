import pytest

from across_server.auth.magic_link import generate, verify
from across_server.auth.tokens import MagicLinkToken


class MockTokenData:
    def __init__(self) -> None:
        self.sub = "user@example.com"
        self.token = "mock-encoded-token"


@pytest.fixture()
def mock_token_data() -> MockTokenData:
    return MockTokenData()


@pytest.fixture(autouse=True)
def mock_magic_link_token(
    monkeypatch: pytest.MonkeyPatch, mock_token_data: MockTokenData
) -> None:
    def to_encode() -> MockTokenData:
        return mock_token_data

    def encode() -> str:
        return mock_token_data.token

    def decode() -> MockTokenData:
        return mock_token_data

    monkeypatch.setattr(
        MagicLinkToken, "to_encode", lambda *args, **kwargs: to_encode()
    )

    monkeypatch.setattr(MagicLinkToken, "encode", lambda *args, **kwargs: encode())

    monkeypatch.setattr(MagicLinkToken, "decode", lambda *args, **kwargs: decode())


class TestGenerateMagicLink:
    def test_should_generate_magic_link(self, mock_token_data: MockTokenData) -> None:
        """Should generate a magic link"""
        assert generate(mock_token_data.sub).__contains__(
            f"/auth/verify?token={mock_token_data.token}"
        )

    def test_should_verify_magic_link(self, mock_token_data: MockTokenData) -> None:
        """Should verify a magic link to return the email of the auth'd user"""
        assert verify(mock_token_data.token) == mock_token_data.sub
