from unittest.mock import MagicMock

import pytest

from across_server.auth.service import AuthService


class TestAuthService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.email = "mockemail"

    def test_generate_magic_link_returns_link(
        self,
        mock_db: MagicMock,
    ) -> None:
        """Should return a new link when calling generate_magic_link"""
        service = AuthService(mock_db)
        link = service.generate_magic_link(self.email)
        assert link.__contains__("/auth/verify?token=mock_token")

    def test_should_throw_error_when_magic_link_generation_fails(
        self, mock_db: MagicMock, mock_magic_link_generate: MagicMock
    ) -> None:
        """Should throw an error when calling generate_magic_link fails"""
        mock_magic_link_generate.side_effect = Exception("Mock Exception")
        with pytest.raises(Exception):
            service = AuthService(mock_db)
            service.generate_magic_link(self.email)
