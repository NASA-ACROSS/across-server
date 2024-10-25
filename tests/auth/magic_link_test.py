# Copyright © 2023 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.

import pytest

from across_server.auth.magic_link import generate
from across_server.auth.tokens import MagicLinkToken


@pytest.fixture(autouse=True)
def mock_magic_link_token(monkeypatch: pytest.MonkeyPatch):
    def mock_to_encode():
        return {"sub": "email@example.com"}

    def mock_encode():
        return "mock-encoded-token"

    monkeypatch.setattr(
        MagicLinkToken, "to_encode", lambda *args, **kwargs: mock_to_encode()
    )

    monkeypatch.setattr(MagicLinkToken, "encode", lambda *args, **kwargs: mock_encode())


class TestGenerateMagicLink:
    def test_should_generate_magic_link(self):
        """Should generate a magic link"""
        assert generate("email@example.com").__contains__(
            "/auth/verify?token=mock-encoded-token"
        )
