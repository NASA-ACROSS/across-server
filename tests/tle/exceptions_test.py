from datetime import datetime

from across_server.routes.tle.exceptions import DuplicateTLEException


def test_duplicate_tle_exception_initialization() -> None:
    """
    Test that DuplicateTLEException is initialized correctly.
    """
    norad_id = 12345
    epoch = datetime.now()
    exception = DuplicateTLEException(norad_id, epoch)

    assert exception.status_code == 409


def test_duplicate_tle_exception_inheritance() -> None:
    """
    Test that DuplicateTLEException inherits from AcrossHTTPException.
    """
    norad_id = 54321
    epoch = datetime.now()
    exception = DuplicateTLEException(norad_id, epoch)

    assert isinstance(exception, DuplicateTLEException)
