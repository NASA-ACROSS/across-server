from typing import Any, MutableMapping

import pytest

from across_server.auth.config import auth_config
from across_server.auth.enums import AuthUserType
from across_server.auth.tokens.access_token import AccessToken, AccessTokenData


@pytest.fixture
def patch_config_secret(monkeypatch: Any) -> None:
    def patch_config_secret_fn(self: Any) -> str:
        return "TEST_SECRET"

    monkeypatch.setattr(
        auth_config,
        "JWT_SECRET_KEY",
        property(patch_config_secret_fn),
        raising=False,
    )


@pytest.fixture(scope="function")
def mock_jwt(patch_config_secret: None) -> str:
    return AccessToken().encode(
        AccessTokenData(
            sub="e2c834a4-232c-420a-985e-eb5bc59aba24",
            type=AuthUserType.USER,
            scopes=[],
            groups=[],
        )
    )


@pytest.fixture(scope="function")
def mock_scope(mock_jwt: str) -> MutableMapping[str, Any]:
    bearer = f"Bearer {mock_jwt}"
    return {
        "client": ("13.13.13.13", "1234"),
        "headers": [
            (
                b"authorization",
                bearer.encode("ascii"),
            )
        ],
    }
