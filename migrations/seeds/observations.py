import random
import uuid
from datetime import datetime, timedelta

from across_server.db.models import Observation

from .instruments import sandy_instrument_calorimeter, instruments
from .schedules import schedules

NUM_OBSERVATIONS_MIN = 1
NUM_OBSERVATIONS_MAX = 100

observations = []

for schedule in schedules:
    for instrument in instruments:
        obs_count = random.randint(NUM_OBSERVATIONS_MIN,NUM_OBSERVATIONS_MAX)
        for obs_num in range(0,obs_count):
            ra = random.random() * 360
            dec = (random.random() * 180) - 90
            sandy_observation = Observation(
                id=uuid.uuid4(),
                instrument=instrument,
                schedule=schedule,
                object_name=f"Krusty Krab #{random.randint(0,10000000)}",
                pointing_ra=ra,
                pointing_dec=dec,
                pointing_position=f"POINT ({ra} {dec})",
                date_range_begin=datetime.now(),
                date_range_end=datetime.now() + timedelta(days=1.0),
                external_observation_id=f"Sandy's Treedome Observation {obs_num} ",
                object_ra=ra,
                object_dec=dec,
                object_position=f"POINT ({ra} {dec})",
                type="imaging",
                status="planned",
                min_wavelength=random.randint(2000,4000),
                max_wavelength=random.randint(4001,6500),
            )
            observations.append(sandy_observation)
            
