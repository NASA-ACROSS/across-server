from datetime import datetime

import pytest
from fastapi import HTTPException

from across_server.routes.v1.tle.schemas import TLE


class TestTLESchemas:
    def test_epoch_calculation(
        self, mock_tle_data: dict, todays_epoch: datetime
    ) -> None:
        tle = TLE(**mock_tle_data)
        assert tle.epoch.year == todays_epoch.year
        assert tle.epoch.month == todays_epoch.month
        assert tle.epoch.day == todays_epoch.day

    def test_epoch_calculation_old_year(self, mock_tle_data_explorer_6: dict) -> None:
        tle = TLE(**mock_tle_data_explorer_6)
        assert tle.epoch.year == 1959

    def test_epoch_invalid_format(self, mock_tle_data_invalid_epoch: dict) -> None:
        tle = TLE(**mock_tle_data_invalid_epoch)
        with pytest.raises(HTTPException) as excinfo:
            tle.epoch
        assert excinfo.value.status_code == 422
        assert "Invalid TLE epoch format" in excinfo.value.detail
