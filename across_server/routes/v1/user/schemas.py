import datetime
import re
import uuid
from typing import Annotated

from fastapi import HTTPException, status
from pydantic import BaseModel, BeforeValidator, EmailStr, field_validator

from ....core.schemas import Permission
from ....core.schemas.base import BaseSchema
from ..group.schemas import GroupBase
from ..role.schemas import RoleBase

# Regular expression to detect HTML tags
HTML_TAG_REGEX = re.compile(r"<[^>]*>|[^\w\s-]")


def validate_no_html(value: str) -> str:
    """Ensure the string contains no HTML tags or other special characters."""
    if HTML_TAG_REGEX.search(value):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid format."
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
    group: GroupBase


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
    @field_validator("email")
    @classmethod
    def validate_allowed_tld(cls, value: EmailStr) -> EmailStr:
        # Imported lazily to avoid an import cycle at module load
        # (util.email <-> auth), and because the check only runs at request time.
        from ....util.email.config import email_config

        allowed = [
            tld.lower().lstrip(".") for tld in email_config.ALLOWED_TOP_LEVEL_DOMAINS
        ]
        if allowed:
            top_level_domain = value.rsplit("@", 1)[-1].rsplit(".", 1)[-1].lower()
            if top_level_domain not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Email domain is not permitted.",
                )
        return value


class UserUpdate(BaseModel):
    first_name: NoHTMLString | None = None
    last_name: NoHTMLString | None = None
    username: NoHTMLString | None = None
