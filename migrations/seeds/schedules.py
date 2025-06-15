import datetime
import hashlib
import random
import uuid

from across_server.core.enums import ScheduleFidelity, ScheduleStatus
from across_server.db.models import Schedule
from across_server.routes.schedule import schemas as ScheduleSchemas

from .telescopes import sandy_telescope
from .users import sandy

schedules = []

def random_date(start_date, end_date):
    """Generates a random date between two given dates.

    Args:
        start_date (datetime): The starting date of the range.
        end_date (datetime): The ending date of the range.

    Returns:
        datetime: A random date within the specified range.
    """
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date

for schedule_num in range(0,100):
    name = random.randint(0,100000000)
    schedule = Schedule(
            id=uuid.uuid4(),
            telescope=sandy_telescope,
            date_range_begin=random_date(datetime.datetime(1993, 3, 13),datetime.datetime.now()),
            date_range_end=random_date(datetime.datetime(1993, 3, 13),datetime.datetime.now()),
            name=f"Bikini Bottom Schedule {name}",
            status=ScheduleStatus.PLANNED.value,
            external_id=f"BikiniBottom_schedule_id_{name}",
            fidelity=ScheduleFidelity.LOW.value,
            created_by_id=sandy.id,
        )
    model_str = ScheduleSchemas.Schedule.from_orm(schedule).model_dump_json()
    checksum = hashlib.sha512(model_str.encode()).hexdigest()
    schedule.checksum = checksum
    schedules.append(schedule)