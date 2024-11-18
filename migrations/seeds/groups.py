import uuid
from across_server.db.models import Group


treedome_space_group = Group(
    id=uuid.uuid4(),
    name="Treedome Space Group",
    short_name="TSG",
)

groups = [treedome_space_group]
