from types import FunctionType
from typing import Any, MutableMapping
from unittest.mock import AsyncMock

import pytest
from ratelimit import Rule

from across_server.core.limiter import (
    authenticate_limit,
    on_limit_exceeded,
    rules,
)


class TestLimiter:
    class TestAuthenticateLimit:
        @pytest.mark.asyncio
        async def test_should_return_tuple(
            self, mock_scope: MutableMapping[str, Any]
        ) -> None:
            return_value = await authenticate_limit(mock_scope)

            assert isinstance(return_value, tuple)

        @pytest.mark.asyncio
        async def test_should_return_limit_key_and_group_defaults_when_scope_missing_all_data(
            self, mock_scope: MutableMapping[str, Any]
        ) -> None:
            mock_scope["client"] = ""
            mock_scope["headers"] = []

            limit_key, group = await authenticate_limit(mock_scope)

            assert limit_key == "unknown anonymous" and group == "default"

        @pytest.mark.asyncio
        async def test_should_return_limit_key_with_ip_address(
            self, mock_scope: MutableMapping[str, Any]
        ) -> None:
            mock_scope["headers"] = []

            limit_key, _ = await authenticate_limit(mock_scope)

            assert limit_key == "13.13.13.13 anonymous"

        @pytest.mark.asyncio
        async def test_should_return_limit_key_with_jwt_sub(
            self, mock_scope: MutableMapping[str, Any]
        ) -> None:
            mock_scope["client"] = ""

            limit_key, _ = await authenticate_limit(mock_scope)

            assert limit_key == "unknown e2c834a4-232c-420a-985e-eb5bc59aba24"

        @pytest.mark.asyncio
        async def test_should_return_group_as_jwt_type(
            self, mock_scope: MutableMapping[str, Any]
        ) -> None:
            _, group = await authenticate_limit(mock_scope)

            assert group == "user"

    class TestOnLimitExceeded:
        def test_should_return_function(self) -> None:
            limit_func = on_limit_exceeded(5)

            assert isinstance(limit_func, FunctionType)

        @pytest.mark.asyncio
        async def test_function_should_send_response(self) -> None:
            mock_retry_after = 5

            limit_func = on_limit_exceeded(mock_retry_after)

            mock_scope = {"client": "", "headers": []}
            mock_receive = AsyncMock()
            mock_send = AsyncMock()

            await limit_func(mock_scope, mock_receive, mock_send)

            mock_send.assert_called()

        @pytest.mark.asyncio
        async def test_function_should_send_response_status_429(self) -> None:
            mock_retry_after = 5

            limit_func = on_limit_exceeded(mock_retry_after)

            mock_scope = {"client": "", "headers": []}
            mock_receive = AsyncMock()
            mock_send = AsyncMock()

            await limit_func(mock_scope, mock_receive, mock_send)

            assert mock_send.mock_calls[0].args[0]["status"] == 429

    class TestRules:
        """Define limiter rule requirements to prevent removal without breaking test"""

        def test_rules_should_have_token_route(self) -> None:
            routes = [*rules]
            route = r".*/token"

            assert route in routes
            assert rules[route].__len__ != 0
            for rule in rules[route]:
                assert isinstance(rule, Rule)

        def test_rules_should_have_catchall_route(self) -> None:
            routes = [*rules]
            route = r".*"

            assert route in routes
            assert rules[route].__len__ != 0
            for rule in rules[r".*"]:
                assert isinstance(rule, Rule)
