from datetime import timedelta
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response
from pydantic import EmailStr


from ..util.decorators import local_only_route
from ..util.email.service import EmailService

from . import schemas, magic_link, tokens, strategies
from .security import extract_creds
from .service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Not found",
        },
    },
)


def setRefreshTokenCookie(response: Response, token: str):
    # Set HttpOnly cookie with refresh token
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days
    )

    return response


@local_only_route(router, path="/local-token", methods=["GET"])
async def local_token(
    email: str,
    service: Annotated[AuthService, Depends(AuthService)],
    access_token: Annotated[tokens.AccessToken, Depends(tokens.AccessToken)],
):
    """
    For local only, directly return an access token for testing purposes
    that expires after 1 day
    """

    auth_user = await service.get_authenticated_user(email=email)

    access_token = tokens.AccessToken()

    token = access_token.encode(
        access_token.to_encode(auth_user),
        expires_delta=timedelta(days=1),
    )

    return token


@router.post("/login", dependencies=[Depends(strategies.webserver_access)])
async def login(
    email: EmailStr,
    email_service: Annotated[EmailService, Depends(EmailService)],
    auth_service: Annotated[AuthService, Depends(AuthService)],
):
    user = await auth_service.get_authenticated_user(email=email)

    link = magic_link.generate(email)

    # Send magic_link to user's email (implement email sending logic)
    await email_service.send(email, {"link": link}, "login-link")

    return {"message": "Magic link sent", "magic_link": link, "user": user}


@router.get("/verify")
async def verify(
    token: str,
    response: Response,
    service: Annotated[AuthService, Depends(AuthService)],
):
    email = magic_link.verify(token)

    auth_user = await service.get_authenticated_user(email=email)
    all_tokens = service.get_auth_tokens(auth_user)

    setRefreshTokenCookie(response, all_tokens["refresh"])

    return schemas.AccessTokenResponse(access_token=all_tokens["access"])


@router.post("/refresh")
async def refresh_token(
    response: Response,
    service: Annotated[AuthService, Depends(AuthService)],
    refresh_token: Annotated[str, Depends(extract_creds)],
):
    token_data = tokens.RefreshToken().decode(refresh_token)

    user = await service.get_authenticated_user(user_id=UUID(token_data.sub))
    auth_tokens = service.get_auth_tokens(user)

    setRefreshTokenCookie(response, auth_tokens["refresh"])

    return schemas.AccessTokenResponse(access_token=auth_tokens["access"])
