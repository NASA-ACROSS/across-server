from uuid import UUID

from pydantic import BaseModel

from ...user.schemas import UserInfo
from ..schemas import GroupRead


class GroupInvite(BaseModel):
    id: UUID
    group: GroupRead
    receiver: UserInfo
    sender: UserInfo


class GroupInviteCreate(BaseModel):
    receiver_email: str


class GroupInviteReadParams(BaseModel):
    id: UUID | None
    sender_id: UUID | None
    receiver_id: UUID | None
    receiver_email: str | None
