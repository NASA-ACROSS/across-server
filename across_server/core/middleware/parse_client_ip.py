from ratelimit.auths.ip import client_ip
from ratelimit.auths.jwt import EmptyInformation
from ratelimit.types import Scope


async def parse_client_ip(scope: Scope) -> str:
    ip = "unknown"

    try:
        ip, _ = await client_ip(scope)
    except EmptyInformation:
        # pull the ip from the x-forwarded-for header if it exists, otherwise it will be unknown
        for name, value in scope.get("headers", []):  # type: bytes, bytes
            if name == b"x-forwarded-for":
                # just in case there is a list of ips, and one is spoofed, we need to take the last one.
                # this assumes that we only have the ALB forwarding requests and no additional proxies. (cloudflare, etc)
                # Example:
                #   Normal (no spoofing): x-forwarded-for: "10.1.13.128"
                #   Spoofed: x-forwarded-for: "1.1.1.1, 2.2.2.2, 10.1.13.128"
                ip = value.decode("utf-8").split(",")[-1].strip()

    return ip
