from ratelimit.auths.ip import client_ip
from ratelimit.auths.jwt import EmptyInformation
from ratelimit.types import Scope


async def parse_client_ip(scope: Scope) -> str:
    ip = "unknown"

    try:
        ip, _ = await client_ip(scope)
    except EmptyInformation:
        # pull the ip from the x-forwarded-for header if it exists, otherwise it will be unknown
        headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
        for name, value in headers:
            if name == b"x-forwarded-for":
                # just in case there is a list of ips, and one is spoofed, we need to take the last one.
                # this assumes that we only have the ALB forwarding requests and no additional proxies. (cloudflare, etc)
                # Example:
                #   Direct calls from proxy: x-forwarded-for: "10.1.13.128 (user), 16.16.16.16 (proxy), 7.7.7.7 (alb)"
                #   Spoofed: x-forwarded-for: "2.2.2.2 (spoof), 10.1.13.128 (user), 16.16.16.16 (proxy), 7.7.7.7 (alb)"
                ip = value.decode("utf-8").split(",")[-2].strip()

    return ip
