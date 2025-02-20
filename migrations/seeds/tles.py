from across_server.db import models
from across_server.routes.tle import schemas

swift_tle_one = models.TLE(
    **schemas.TLE(
        satellite_name="SWIFT",
        norad_id=28485,
        tle1="1 28485U 12345A   04325.95833333  .00002127  00000-0  20720-3 0    77",
        tle2="2 28485 020.5578 139.4813 0014709 229.4254 071.4033 14.91215581000018",
    ).model_dump()
)

swift_tle_two = models.TLE(
    **schemas.TLE(
        satellite_name="SWIFT",
        norad_id=28485,
        tle1="1 28485U 04047A   25038.03159117  .00027471  00000+0  86373-3 0  9997",
        tle2="2 28485  20.5557 285.8116 0006385  93.6070 266.5099 15.31053389110064",
    ).model_dump()
)

tles = [swift_tle_one, swift_tle_two]
