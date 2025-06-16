import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Security, status

from ....auth import magic_link
from ....auth.schemas import AuthUser
from ....auth.strategies import group_access
from ....util.email.service import EmailService
from ...user.service import UserService
from ..service import GroupService
from . import schemas
from .service import GroupInviteService

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

router = APIRouter(
    prefix="/group/{group_id}",
    tags=["Group Invite"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The group or invite does not exist.",
        },
    },
)


@router.get(
    "/invite",
    summary="Read group invites",
    description="Read all group invites for a group",
    operation_id="get_invites",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.GroupInvite],
            "description": "A list of group invites",
        },
    },
    dependencies=[Security(group_access, scopes=["group:user:write"])],
)
async def get_many(
    service: Annotated[GroupInviteService, Depends(GroupInviteService)],
    group_id: uuid.UUID,
) -> list[schemas.GroupInvite]:
    group_invite_models = await service.get_many(group_id)
    return [
        schemas.GroupInvite.model_validate(invite, from_attributes=True)
        for invite in group_invite_models
    ]


@router.get(
    "/invite/{invite_id}",
    summary="Read a group invite",
    description="Read a single group invite by ID",
    operation_id="get_invite",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.GroupInvite,
            "description": "The requested group invite",
        },
    },
    dependencies=[Security(group_access, scopes=["group:user:write"])],
)
async def get(
    service: Annotated[GroupInviteService, Depends(GroupInviteService)],
    group_id: uuid.UUID,
    invite_id: uuid.UUID,
) -> schemas.GroupInvite:
    group_invite = await service.get(invite_id, group_id)
    return schemas.GroupInvite.model_validate(group_invite, from_attributes=True)


@router.post(
    "/invite",
    summary="Create and send a group invite",
    description="Create and send a group invite to a user",
    operation_id="send_invite",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.GroupInvite,
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.GroupInvite,
            "description": "The created group invite",
        },
    },
)
async def create(
    group_invite_service: Annotated[GroupInviteService, Depends(GroupInviteService)],
    group_service: Annotated[GroupService, Depends(GroupService)],
    user_service: Annotated[UserService, Depends(UserService)],
    email_service: Annotated[EmailService, Depends(EmailService)],
    auth_user: Annotated[AuthUser, Security(group_access, scopes=["group:user:write"])],
    group_id: uuid.UUID,
    data: schemas.GroupInviteCreate,
) -> schemas.GroupInvite:
    group = await group_service.get(group_id)
    receiver_user_model = await user_service.get_by_email(email=data.receiver_email)
    sender_user_model = await user_service.get(auth_user.id)
    group_invite = await group_invite_service.send(
        auth_user.id, group, receiver_user_model
    )

    # Construct login link for receiver
    receiver_login_link = magic_link.generate(data.receiver_email)

    invitation_email_body = email_service.construct_group_invitation_email(
        sender_user_model, receiver_user_model, group, receiver_login_link
    )

    try:
        await email_service.send(
            recipients=[receiver_user_model.email],
            subject="NASA ACROSS Group Invitation",
            content_html=invitation_email_body,
        )
    except Exception as e:
        logger.error("Email service failed to send group invitation email", e=e)

    return schemas.GroupInvite.model_validate(group_invite, from_attributes=True)


@router.delete(
    "/invite/{invite_id}",
    summary="Delete a group invite",
    description="Delete a group invite by ID",
    operation_id="delete_invite",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(group_access, scopes=["group:user:write"])],
)
async def delete(
    group_invite_service: Annotated[GroupInviteService, Depends(GroupInviteService)],
    invite_id: uuid.UUID,
    group_id: uuid.UUID,
) -> None:
    invite = await group_invite_service.get(invite_id, group_id)
    await group_invite_service.delete(invite)
