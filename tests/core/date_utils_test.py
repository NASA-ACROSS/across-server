from datetime import datetime, timedelta, timezone

import pytest
from dateutil import tz

from across_server.core.date_utils import convert_to_utc


class TestConvertToUTC:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_datetime = datetime(
            year=2025, month=1, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc
        )
        self.mock_date_string = "2025-01-01T00:00:00.0000Z"
        self.mock_datetime_tz_naive = datetime(
            year=2025, month=1, day=1, hour=0, minute=0, second=0, tzinfo=None
        )
        self.mock_date_string_tz_naive = "2025-01-01T00:00:00.0000"
        self.mock_datetime_gsfc = datetime(
            year=2024,
            month=12,
            day=31,
            hour=19,
            minute=0,
            second=0,
            tzinfo=tz.tzoffset("America/DC", timedelta(hours=-5)),
        )
        self.mock_date_string_gsfc = "2024-12-31T19:00:00.0000-05:00"

    def test_should_handle_datetimes(self):
        """Should convert timezone-aware datetime to timezone-naive datetime"""
        assert convert_to_utc(self.mock_datetime) == self.mock_datetime.replace(
            tzinfo=None
        )

    def test_should_handle_strings(self):
        """Should convert timezone-aware string to timezone-naive datetime"""
        assert convert_to_utc(self.mock_date_string) == self.mock_datetime.replace(
            tzinfo=None
        )

    def test_should_handle_tz_naive_datetimes(self):
        """Should convert timezone-naive datetime to timezone-naive datetime"""
        assert (
            convert_to_utc(self.mock_datetime_tz_naive) == self.mock_datetime_tz_naive
        )

    def test_should_handle_tz_naive_strings(self):
        """Should convert timezone-naive string to timezone-naive datetime"""
        assert (
            convert_to_utc(self.mock_date_string_tz_naive)
            == self.mock_datetime_tz_naive
        )

    def test_should_convert_timezones(self):
        """Should convert non-UTC datetimes to UTC before removing timezone"""
        assert convert_to_utc(self.mock_datetime_gsfc) == self.mock_datetime_tz_naive

    def test_should_convert_timezone_strings(self):
        """Should convert non-UTC strings to UTC before removing timezone"""
        assert convert_to_utc(self.mock_date_string_gsfc) == self.mock_datetime_tz_naive

    def test_should_raise_exception_when_input_not_date(self):
        """should raise an exception when input is not a datetime or iso format string"""
        with pytest.raises(ValueError):
            convert_to_utc("twenty twenty four")
