import uuid
from datetime import datetime, timedelta

from across_server.core.enums import DepthUnit, ObservationRequestStatus
from across_server.db.models import ObservationRequest

from .instruments import sandy_instrument_calorimeter
from .observing_proposal import sandy_proposal

krusty_too = ObservationRequest(
    id=uuid.UUID("6450ad6e-e185-4313-83b2-d6ed15bc11ca"),
    instrument=sandy_instrument_calorimeter,
    science_justification="Krusty Krab is being threatened by Plankton, and we need to observe it to determine the best course of action to save the business.",
    object_name="Krusty Krab TOO",
    object_brightness=5.5,
    object_brightness_unit=DepthUnit.AB_MAG.value,
    object_ra=123.456,
    object_dec=-78.901,
    object_position="POINT (123.456 -78.901)",
    date_range_begin=datetime.now(),
    date_range_end=datetime.now() + timedelta(days=1.0),
    status=ObservationRequestStatus.PENDING.value,
    status_reason="Awaiting review",
    observing_proposal=sandy_proposal,
    parent_id=uuid.UUID("6450ad6e-e185-4313-83b2-d6ed15bc11ca"),
    anonymize=False,
    is_too=True,
)

observation_requests = [krusty_too]
