import uuid
from datetime import datetime, timedelta

from across_server.db.models import Observation

from .instruments import sandy_instrument
from .schedules import sandy_schedule

sandy_observation = Observation(
    id=uuid.uuid4(),
    instrument=sandy_instrument,
    schedule=sandy_schedule,
    object_name="Krusty Krab",
    pointing_ra=123.456,
    pointing_dec=-78.901,
    pointing_position="POINT (123.456 -78.901)",
    date_range_begin=datetime.now(),
    date_range_end=datetime.now() + timedelta(days=1.0),
    external_observation_id="Sandy's Treedome Observations",
    object_ra=123.567,
    object_dec=-78.876,
    object_position="POINT (123.567 -78.876)",
    type="imaging",
    status="planned",
    min_wavelength=4500,
    max_wavelength=6500,
)

observations = [sandy_observation]
