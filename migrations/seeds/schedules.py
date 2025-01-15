import uuid

from across_server.db.models import Schedule

from .instruments import sandy_instrument

sandy_schedule = Schedule(id=uuid.uuid4(), instrument=sandy_instrument)

schedules = [sandy_schedule]
