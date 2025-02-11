import pytest

from across_server.routes.tle import schemas


def test_tle_schema_check_epoch_and_other_fields(mock_tle_data, todays_epoch):
    """
    Test TLE schema property validations.
    This test verifies that the TLE schema correctly initializes and validates its fields,
    particularly checking that the epoch field is properly converted from ISO format
    and all other fields match the input data.

    Parameters
    ----------
    mock_tle_data : dict
        Mock TLE data containing satellite_name, norad_id, tle1, tle2, and epoch fields

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If any field validation fails or if epoch conversion is incorrect
    """

    tle_schema = schemas.TLE(
        satellite_name=mock_tle_data["satellite_name"],
        norad_id=mock_tle_data["norad_id"],
        tle1=mock_tle_data["tle1"],
        tle2=mock_tle_data["tle2"],
    )

    test_data = [
        ("epoch", lambda x: todays_epoch),
        ("satellite_name", lambda x: mock_tle_data[x]),
        ("norad_id", lambda x: mock_tle_data[x]),
        ("tle1", lambda x: mock_tle_data[x]),
        ("tle2", lambda x: mock_tle_data[x]),
    ]

    @pytest.mark.parametrize("field,expected", test_data)
    def check_field(field, expected):
        if field == "epoch":
            # As Epoch is converted into days with 8 decimal places, we need to
            # compare it with a tolerance of 0.001 seconds when converting back
            assert (
                abs(getattr(tle_schema, field) - expected(field)).total_seconds()
                < 0.001
            )
        else:
            assert getattr(tle_schema, field) == expected(field)

    for field, expected in test_data:
        check_field(field, expected)
