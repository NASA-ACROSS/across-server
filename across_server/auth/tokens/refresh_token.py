from datetime import timedelta
from uuid import UUID

from ..config import auth_config
from .base_token import Token, TokenData


class RefreshTokenData(TokenData[str]):
    """
    Payload of the decoded JWT as a refresh token. This only holds the `sub` and `exp` to verify identity.
    Its only purpose is to obtain new access tokens once they have expired.

    Params:
        sub: string UUID of the user.
        exp: expiration of the token.
    """

    pass


# Refresh Token class
class RefreshToken(Token[RefreshTokenData, UUID]):
    key: str = auth_config.JWT_REFRESH_SECRET_KEY

    @property
    def data_model(self) -> type[RefreshTokenData]:
        return RefreshTokenData

    def encode(
        self,
        data: RefreshTokenData,
        expires_delta: timedelta = timedelta(days=auth_config.REFRESH_EXPIRES_IN_DAYS),
    ) -> str:
        return super().encode(
            data,
            expires_delta=expires_delta,
        )

    def to_encode(self, user_id: UUID) -> RefreshTokenData:
        return RefreshTokenData(sub=str(user_id))
