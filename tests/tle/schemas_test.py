from datetime import datetime

import pytest

from across_server.routes.tle import schemas


@pytest.mark.asyncio
async def test_tle_schema_check_epoch_and_other_fields(mock_tle_data):
    tle_schema = schemas.TLE(
        satellite_name=mock_tle_data["satellite_name"],
        norad_id=mock_tle_data["norad_id"],
        tle1=mock_tle_data["tle1"],
        tle2=mock_tle_data["tle2"],
    )
    assert tle_schema.epoch == datetime.fromisoformat(mock_tle_data["epoch"])
    assert tle_schema.satellite_name == mock_tle_data["satellite_name"]
    assert tle_schema.norad_id == mock_tle_data["norad_id"]
    assert tle_schema.tle1 == mock_tle_data["tle1"]
    assert tle_schema.tle2 == mock_tle_data["tle2"]
