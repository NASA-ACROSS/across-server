from uuid import UUID, uuid4

import pytest

from across_server.auth.schemas import AuthUser, Group, PrincipalType


@pytest.fixture
def mock_group_admin() -> AuthUser:
    return AuthUser(
        id=uuid4(),
        scopes=[],
        groups=[
            Group(
                id=UUID("81ea7ac1-da07-49e3-b1b7-fb08b6034c15"),
                scopes=["group:observation_request:write"],
                is_admin=True,
            )
        ],
        type=PrincipalType.USER,
    )


@pytest.fixture
def mock_submitter() -> AuthUser:
    return AuthUser(
        id=uuid4(),
        scopes=[],
        groups=[],
        type=PrincipalType.USER,
    )
