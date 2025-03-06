from pydantic import EmailStr

from ..config import auth_config
from .base_token import Token, TokenData


class MagicLinkTokenData(TokenData[EmailStr]):
    """
    Payload of a decoded JWT for a magic link.

    It is only used for login purposes to obtain an access token and refresh token.

    Params:
        sub: email of the user.
        exp: expiration of the token.
    """

    pass


# Magic Link Token class
class MagicLinkToken(Token[MagicLinkTokenData, EmailStr]):
    key = auth_config.JWT_MAGIC_LINK_SECRET_KEY

    @property
    def data_model(self) -> type[MagicLinkTokenData]:
        return MagicLinkTokenData

    def to_encode(self, email: EmailStr) -> MagicLinkTokenData:
        return MagicLinkTokenData(sub=email)
