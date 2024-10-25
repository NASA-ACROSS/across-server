from typing import List, Type

from .base_token import TokenData, Token
from ..config import auth_config
from ..schemas import AuthUser, Group


class AccessTokenData(TokenData[str]):
    """
    Payload of a decoded JWT as an access token.

    This is the main token that is used for accessing routes.

    Params:
        sub: string UUID of the user.
        exp: expiration of the token.
        scopes: scopes from the user's roles.
        groups: groups the user belongs to and their associated scopes.
    """

    scopes: List[str]
    groups: List[Group]


class AccessToken(Token[AccessTokenData, AuthUser]):
    key = auth_config.JWT_SECRET_KEY

    @property
    def data_model(self) -> Type[AccessTokenData]:
        return AccessTokenData

    def to_encode(self, auth_user: AuthUser):
        return AccessTokenData(sub=str(auth_user.id), **auth_user.model_dump())
