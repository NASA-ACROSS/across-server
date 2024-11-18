from pydantic import EmailStr

from .tokens.magic_token import MagicLinkToken

from ..core.config import config as core_config


def generate(email: EmailStr) -> str:
    """
    Generate a magic link. This uses a JWT with a 15 minute expiration.
    """
    token = MagicLinkToken()
    encoded_token = token.encode(data=token.to_encode(email))

    return f"{core_config.base_url()}/auth/verify?token={encoded_token}"


def verify(token: str) -> EmailStr:
    return MagicLinkToken().decode(token).sub
