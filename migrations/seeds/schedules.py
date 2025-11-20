import datetime
import hashlib
import uuid

from across_server.core.enums import ScheduleFidelity, ScheduleStatus
from across_server.db.models import Schedule

from .telescopes import sandy_telescope
from .users import sandy

sandy_schedule = Schedule(
    id=uuid.UUID("3f8a9900-158d-4227-b689-546a37e458ba"),
    telescope=sandy_telescope,
    date_range_begin=datetime.datetime.now(),
    date_range_end=datetime.datetime.now() + datetime.timedelta(days=1),
    name="Bikini Bottom Schedule",
    status=ScheduleStatus.PLANNED.value,
    external_id="BikiniBottom_schedule_id_1234",
    fidelity=ScheduleFidelity.LOW.value,
    created_by_id=sandy.id,
    checksum=hashlib.sha512("Sandy's Schedule".encode()).hexdigest(),
    observation_count=1,
)

schedules = [sandy_schedule]
