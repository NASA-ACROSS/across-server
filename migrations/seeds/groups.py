import uuid

from across_server.db.models import Group

treedome_space_group = Group(
    id=uuid.UUID("81ea7ac1-da07-49e3-b1b7-fb08b6034c15"),
    name="Treedome Space Group",
    short_name="TSG",
)

groups = [treedome_space_group]
