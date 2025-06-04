from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from across_server.auth.schemas import GrantType
from across_server.auth.security import authenticate_grant_type


class TestSecurity:
    class TestAuthenticateGrantType:
        @pytest.mark.asyncio
        async def test_should_raise_exception_when_no_grant_type(
            self, mock_auth_service: MagicMock
        ) -> None:
            with pytest.raises(HTTPException):
                await authenticate_grant_type(
                    mock_auth_service,
                    "testBearerCredentials",
                    HTTPBasicCredentials(
                        username="testUsername", password="testPassword"
                    ),
                    None,  # type: ignore
                )

        @pytest.mark.asyncio
        async def test_should_raise_exception(
            self, mock_auth_service: MagicMock
        ) -> None:
            with pytest.raises(HTTPException):
                await authenticate_grant_type(mock_auth_service, None, None, None)  # type: ignore

        @pytest.mark.asyncio
        async def test_should_call_authenticate_service_account_when_client_credentials(
            self, mock_auth_service: MagicMock
        ) -> None:
            await authenticate_grant_type(
                mock_auth_service,
                "testBearerCredentials",
                HTTPBasicCredentials(username="testUsername", password="testPassword"),
                GrantType.CLIENT_CREDENTIALS,
            )
            mock_auth_service.authenticate_service_account.assert_called_once()

        @pytest.mark.asyncio
        async def test_should_call_authenticate_user_when_jwt(
            self, mock_auth_service: MagicMock
        ) -> None:
            await authenticate_grant_type(
                mock_auth_service,
                "testBearerCredentials",
                HTTPBasicCredentials(username="testUsername", password="testPassword"),
                GrantType.JWT,
            )
            mock_auth_service.authenticate_user.assert_called_once()
