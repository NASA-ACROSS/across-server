from typing import Dict, Sequence, Tuple

from ratelimit import Rule
from ratelimit.auths.ip import client_ip
from ratelimit.auths.jwt import EmptyInformation, create_jwt_auth
from ratelimit.types import Scope

from ..auth.config import auth_config

jwt_auth = create_jwt_auth(
    auth_config.JWT_SECRET_KEY, auth_config.JWT_ALGORITHM, "sub", "type"
)


async def authenticate_limit(scope: Scope) -> Tuple[str, str]:
    ip: str

    try:
        ip, default = await client_ip(scope)
    except EmptyInformation:
        ip = "localhost"

    user: str  # uuid
    group: str  # "user" or "service_account" if user, else "default"

    try:
        user, group = await jwt_auth(scope)
    except EmptyInformation:
        user = "anonymous"
        group = "default"

    user_limit_key = f"{ip}:{user}"

    return user_limit_key, group


limit_config: Dict[str, Sequence[Rule]] = {
    r".*": [
        Rule(minute=10, group="default"),
        Rule(second=5, group="user"),
        Rule(second=10, group="service_account"),
    ],
}
