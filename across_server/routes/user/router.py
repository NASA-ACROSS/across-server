import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, status

from ... import auth, db
from ...util.email.service import EmailService
from ..group.invite.service import GroupInviteService
from ..group.service import GroupService
from ..user.invite.service import UserInviteService
from . import schemas
from .service import UserService

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.User],
    operation_id="get_users",
)
async def get_many(
    service: Annotated[UserService, Depends(UserService)],
) -> list[schemas.User]:
    many_user_models = await service.get_many()
    return [schemas.User.model_validate(user_model) for user_model in many_user_models]


@router.get(
    "/{user_id}",
    summary="Read a user",
    description="Read a user by a user ID.",
    operation_id="get_user",
    status_code=status.HTTP_200_OK,
    response_model=schemas.User,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.User,
            "description": "Return a user",
        },
    },
    dependencies=[Depends(auth.strategies.self_access)],
)
async def get(
    service: Annotated[UserService, Depends(UserService)], user_id: uuid.UUID
) -> schemas.User:
    user_model = await service.get(user_id)

    for invite in user_model.received_invites:
        await invite.awaitable_attrs.sender

    return schemas.User.model_validate(user_model, from_attributes=True)


@router.post(
    "/",
    summary="Create a user",
    description="Create a new user for ACROSS.",
    operation_id="create_user",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {},
    },
    dependencies=[Depends(auth.strategies.webserver_access)],
)
async def create(
    user_service: Annotated[UserService, Depends(UserService)],
    auth_service: Annotated[auth.AuthService, Depends(auth.AuthService)],
    email_service: Annotated[EmailService, Depends(EmailService)],
    data: schemas.UserCreate,
) -> None:
    user = await user_service.create(data)
    magic_link = auth_service.generate_magic_link(user.email)
    verification_email_body = email_service.construct_verification_email(
        user, magic_link
    )

    try:
        await email_service.send(
            recipients=[user.email],
            subject="NASA ACROSS Login Link",
            content_html=verification_email_body,
        )
    except Exception as e:
        logger.error("Email service failed to send user registration email", e=e)


@router.patch(
    "/{user_id}",
    summary="Update a user",
    description="Update a user's information for the allowed properties.",
    operation_id="update_user",
    status_code=status.HTTP_200_OK,
    response_model=schemas.User,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.User,
            "description": "The updated user",
        },
    },
)
async def update(
    auth_user: Annotated[db.models.User, Depends(auth.strategies.self_access)],
    service: Annotated[UserService, Depends(UserService)],
    user_id: uuid.UUID,
    data: schemas.UserUpdate,
) -> schemas.User:
    user_model = await service.update(user_id, data, modified_by=auth_user)
    return schemas.User.model_validate(user_model)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
    operation_id="delete_user",
    description="Permanently delete a user from the ACROSS system. This will also delete all associated relations for the user.",
    response_model=schemas.User,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.User,
            "description": "Upon successful deletion, the user is returned",
        },
    },
)
async def delete(
    service: Annotated[UserService, Depends(UserService)],
    user_id: uuid.UUID,
) -> schemas.User:
    user_model = await service.delete(user_id)
    return schemas.User.model_validate(user_model)


# Invites
@router.get(
    "/{user_id}/invite",
    summary="Read a user's group invites",
    description="Read a user's group invites by a user ID.",
    operation_id="get_group_invites",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.GroupInvite],
            "description": "List of group invites for a user id",
        },
    },
    dependencies=[Depends(auth.strategies.self_access)],
)
async def get_invites(
    service: Annotated[UserInviteService, Depends(UserInviteService)],
    user_id: uuid.UUID,
) -> list[schemas.GroupInvite]:
    group_invites = await service.get_many(user_id)
    return [schemas.GroupInvite.model_validate(invite) for invite in group_invites]


@router.patch(
    "/{user_id}/invite/{invite_id}",
    summary="Accept a group invitation",
    description="Accept a group invitation to join a user group.",
    operation_id="accept_invite",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "The group invitation has been accepted",
        },
    },
    dependencies=[Depends(auth.strategies.self_access)],
)
async def accept_invite(
    user_invite_service: Annotated[UserInviteService, Depends(UserInviteService)],
    group_invite_service: Annotated[GroupInviteService, Depends(GroupInviteService)],
    user_id: uuid.UUID,
    invite_id: uuid.UUID,
) -> None:
    group_invite = await user_invite_service.get(user_id, invite_id)
    await group_invite_service.accept(group_invite)


@router.delete(
    "/{user_id}/invite/{invite_id}",
    summary="Decline a group invitation",
    description="Decline a group invitation to refuse joining a user group.",
    operation_id="decline_invite",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "The group invitation has been declined",
        },
    },
    dependencies=[Depends(auth.strategies.self_access)],
)
async def decline_invite(
    user_invite_service: Annotated[UserInviteService, Depends(UserInviteService)],
    group_invite_service: Annotated[GroupInviteService, Depends(GroupInviteService)],
    user_id: uuid.UUID,
    invite_id: uuid.UUID,
) -> None:
    group_invite = await user_invite_service.get(user_id, invite_id)
    await group_invite_service.delete(group_invite)


# Leave Group
@router.delete(
    "/{user_id}/group/{group_id}",
    summary="Leave a group",
    description="Leave a group by id",
    operation_id="leave_group",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Successfully left the group",
        },
    },
    dependencies=[Depends(auth.strategies.self_access)],
)
async def leave_group(
    user_service: Annotated[UserService, Depends(UserService)],
    group_service: Annotated[GroupService, Depends(GroupService)],
    user_id: uuid.UUID,
    group_id: uuid.UUID,
) -> None:
    user = await user_service.get(user_id)
    await group_service.remove_user(user, group_id)
