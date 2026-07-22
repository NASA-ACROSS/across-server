from typing import Any

import pytest
from fastapi import HTTPException

from across_server.routes.v1.user.schemas import UserBase, UserCreate
from across_server.util.email.config import email_config


class TestUserBaseSchema:
    """Test suite for the UserBase schema"""

    def test_schema_data_no_html(self, mock_user_json: dict[str, Any]) -> None:
        """
        Should return a validated schema when data has no
        HTML or other prohibited special characters
        """
        mock_user_schema = UserBase(**mock_user_json)
        assert mock_user_schema.username == mock_user_json["username"]

    def test_schema_data_with_special_character(
        self, mock_user_json: dict[str, Any]
    ) -> None:
        """
        Should raise a 422 exception when data contains a special character
        """
        mock_user_json["username"] = "mockuser!!!"
        with pytest.raises(HTTPException):
            UserBase(**mock_user_json)

    def test_schema_data_with_html(self, mock_user_json: dict[str, Any]) -> None:
        """
        Should raise a 422 exception when data contains html
        """
        mock_user_json["first_name"] = "<b>Mock</b>"
        with pytest.raises(HTTPException):
            UserBase(**mock_user_json)

    def test_schema_data_with_dash_allowed(
        self, mock_user_json: dict[str, Any]
    ) -> None:
        """Should return a validated schema when `-` is in the data"""
        mock_user_json["last_name"] = "User-Person"
        mock_user_schema = UserBase(**mock_user_json)
        assert mock_user_schema.last_name == mock_user_json["last_name"]

    def test_schema_data_with_underscore_allowed(
        self, mock_user_json: dict[str, Any]
    ) -> None:
        """Should return a validated schema when `-` is in the data"""
        mock_user_json["username"] = "mock_user"
        mock_user_schema = UserBase(**mock_user_json)
        assert mock_user_schema.username == mock_user_json["username"]


class TestUserCreateSchema:
    """Test suite for the UserCreate top-level-domain gate"""

    def test_allows_any_tld_when_list_empty(
        self, mock_user_json: dict[str, Any], monkeypatch: Any
    ) -> None:
        """An empty ALLOWED_TOP_LEVEL_DOMAINS means no restriction"""
        monkeypatch.setattr(email_config, "ALLOWED_TOP_LEVEL_DOMAINS", [])
        user = UserCreate(**mock_user_json)
        assert user.email == mock_user_json["email"]

    def test_allows_email_with_permitted_tld(
        self, mock_user_json: dict[str, Any], monkeypatch: Any
    ) -> None:
        """Should validate when the email's TLD is on the allow-list"""
        monkeypatch.setattr(email_config, "ALLOWED_TOP_LEVEL_DOMAINS", ["gov", " .edu"])
        mock_user_json["email"] = "sandy@bikinibottom.gov"
        user = UserCreate(**mock_user_json)
        assert user.email == "sandy@bikinibottom.gov"

    def test_rejects_email_with_unpermitted_tld(
        self, mock_user_json: dict[str, Any], monkeypatch: Any
    ) -> None:
        """Should raise a 422 when the email's TLD is not on the allow-list"""
        monkeypatch.setattr(email_config, "ALLOWED_TOP_LEVEL_DOMAINS", ["gov"])
        mock_user_json["email"] = "sandy@treedome.space"
        with pytest.raises(HTTPException):
            UserCreate(**mock_user_json)

    def test_tld_check_is_case_insensitive(
        self, mock_user_json: dict[str, Any], monkeypatch: Any
    ) -> None:
        """Should match TLDs regardless of case and a leading dot in config"""
        monkeypatch.setattr(email_config, "ALLOWED_TOP_LEVEL_DOMAINS", [".GOV"])
        mock_user_json["email"] = "sandy@bikinibottom.GoV"
        user = UserCreate(**mock_user_json)
        assert user.email == "sandy@bikinibottom.gov"
