from typing import Any

import pytest
from fastapi import HTTPException

from across_server.routes.user.schemas import UserBase


class TestUserBaseSchema:
    """Test suite for the UserBase schema"""

    def test_schema_data_no_html(self, mock_user_data: dict[str, Any]) -> None:
        """
        Should return a validated schema when data has no
        HTML or other prohibited special characters
        """
        mock_user_schema = UserBase(**mock_user_data)
        assert mock_user_schema.username == mock_user_data["username"]

    def test_schema_data_with_special_character(
        self, mock_user_data: dict[str, Any]
    ) -> None:
        """
        Should raise a 422 exception when data contains a special character
        """
        mock_user_data["username"] = "mockuser!!!"
        with pytest.raises(HTTPException):
            UserBase(**mock_user_data)

    def test_schema_data_with_html(self, mock_user_data: dict[str, Any]) -> None:
        """
        Should raise a 422 exception when data contains html
        """
        mock_user_data["first_name"] = "<b>Mock</b>"
        with pytest.raises(HTTPException):
            UserBase(**mock_user_data)

    def test_schema_data_with_dash_allowed(
        self, mock_user_data: dict[str, Any]
    ) -> None:
        """Should return a validated schema when `-` is in the data"""
        mock_user_data["last_name"] = "User-Person"
        mock_user_schema = UserBase(**mock_user_data)
        assert mock_user_schema.last_name == mock_user_data["last_name"]

    def test_schema_data_with_underscore_allowed(
        self, mock_user_data: dict[str, Any]
    ) -> None:
        """Should return a validated schema when `-` is in the data"""
        mock_user_data["username"] = "mock_user"
        mock_user_schema = UserBase(**mock_user_data)
        assert mock_user_schema.username == mock_user_data["username"]
