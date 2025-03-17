from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from pydantic import EmailStr

from ..util.decorators import local_only_route
from ..util.email.service import EmailService
from . import magic_link, schemas, strategies, tokens
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


def setRefreshTokenCookie(response: Response, token: str) -> Response:
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
) -> str:
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
) -> dict:
    user = await auth_service.get_authenticated_user(email=email)

    link = magic_link.generate(email)

    # Send magic_link to user's email
    login_email_body = email_service.construct_login_email(user, link)

    await email_service.send(
        recipients=[email],
        subject="NASA ACROSS Account Login",
        content_html=login_email_body,
    )

    return {"message": "Magic link sent", "magic_link": link, "user": user}


@router.get("/verify")
async def verify(
    token: str,
    response: Response,
    service: Annotated[AuthService, Depends(AuthService)],
) -> schemas.AccessTokenResponse:
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
) -> schemas.AccessTokenResponse:
    token_data = tokens.RefreshToken().decode(refresh_token)

    user = await service.get_authenticated_user(user_id=UUID(token_data.sub))
    auth_tokens = service.get_auth_tokens(user)

    setRefreshTokenCookie(response, auth_tokens["refresh"])

    return schemas.AccessTokenResponse(access_token=auth_tokens["access"])
