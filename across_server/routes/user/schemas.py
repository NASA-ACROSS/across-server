import datetime
import re
import uuid
from typing import Annotated

from fastapi import HTTPException, status
from pydantic import BaseModel, BeforeValidator, EmailStr

from ...core.schemas import Permission
from ...core.schemas.base import BaseSchema
from ..role.schemas import RoleBase

# Regular expression to detect HTML tags
HTML_TAG_REGEX = re.compile(r"<[^>]*>|[^\w\s-]")


def validate_no_html(value: str) -> str:
    """Ensure the string contains no HTML tags or other special characters."""
    if HTML_TAG_REGEX.search(value):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid format."
        )
    return value


NoHTMLString = Annotated[str, BeforeValidator(validate_no_html)]


class UserBase(BaseSchema):
    username: NoHTMLString
    first_name: NoHTMLString
    last_name: NoHTMLString
    email: EmailStr


class UserInfo(UserBase):
    id: uuid.UUID
    pass


# This is explicitly defined due to
#   A) parent data should define what data from the child it needs
#   B) pydantic does not handle circular imports, so even if we
#      wanted to import these schemas, we can't.
class GroupInviteGroupDetails(BaseSchema):
    id: uuid.UUID
    name: str
    short_name: str
    created_on: datetime.datetime


class GroupInvite(BaseSchema):
    id: uuid.UUID
    group: GroupInviteGroupDetails
    sender: UserInfo


class GroupRole(BaseSchema):
    id: uuid.UUID
    name: str
    permissions: list[Permission]


class Group(BaseSchema):
    id: uuid.UUID
    name: str
    short_name: str
    roles: list[GroupRole]


class User(UserBase):
    id: uuid.UUID
    groups: list[Group]
    roles: list[RoleBase]
    group_roles: list[GroupRole]
    received_invites: list[GroupInvite]


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    first_name: NoHTMLString | None = None
    last_name: NoHTMLString | None = None
    username: NoHTMLString | None = None
