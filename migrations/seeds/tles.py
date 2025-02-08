from datetime import datetime, timedelta

from across_server.db.models import TLE


def tle_date_to_datetime(tleepoch):
    # Convert 2-digit year to 4-digit year
    tleyear = int(tleepoch[0:2])
    year = 2000 + tleyear if tleyear < 57 else 1900 + tleyear

    # Convert day of year into float
    day_of_year = float(tleepoch[2:])

    # Return Time epoch
    return datetime(year, 1, 1) + timedelta(days=day_of_year - 1)


swift_tle_one = TLE(
    satellite_name="SWIFT",
    epoch=tle_date_to_datetime("04325.95833333"),
    norad_id=28485,
    tle1="1 28485U 12345A   04325.95833333  .00002127  00000-0  20720-3 0    77",
    tle2="2 28485 020.5578 139.4813 0014709 229.4254 071.4033 14.91215581000018",
)

swift_tle_two = TLE(
    satellite_name="SWIFT",
    epoch=tle_date_to_datetime("25038.03159117"),
    norad_id=28485,
    tle1="1 28485U 04047A   25038.03159117  .00027471  00000+0  86373-3 0  9997",
    tle2="2 28485  20.5557 285.8116 0006385  93.6070 266.5099 15.31053389110064",
)

tles = [swift_tle_one, swift_tle_two]
