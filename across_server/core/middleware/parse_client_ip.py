from ipaddress import ip_address

import structlog
from ratelimit.auths.jwt import EmptyInformation
from ratelimit.types import Scope

from across_server.core.config import config

logger = structlog.get_logger()


async def client_ip(scope: Scope) -> tuple[str, str]:
    """
    parse ip
    """
    logger.debug(
        "Parsing client IP", client=scope["client"], headers=scope.get("headers", [])
    )

    real_ip = ""
    if scope["client"]:
        ip, port = tuple(scope["client"])
        if ip_address(ip).is_global:
            real_ip = ip
    else:
        raise EmptyInformation(scope)

    for name, value in scope["headers"]:  # type: bytes, bytes
        if name == b"x-real-ip":
            ip = value.decode("utf8")

        if not real_ip and ip_address(ip).is_global:
            real_ip = ip

    if not real_ip:
        raise EmptyInformation(scope)
    return real_ip, "default"


async def parse_client_ip(scope: Scope) -> str:
    ip = "unknown"

    try:
        ip, _ = await client_ip(scope)
    except EmptyInformation:
        # pull the ip from the x-forwarded-for header if it exists, otherwise it will be unknown
        headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
        for name, value in headers:
            if name == b"x-forwarded-for":
                # just in case there is a list of ips, and one is spoofed, we need to account for it.
                # We currently have the rev proxy and the ALB forwarding requests and no additional proxies. (cloudflare, etc)
                # The alb will be the final request, so that will simply be the requester IP.
                # Example:
                #   Direct calls from proxy: x-forwarded-for: "10.1.13.128 (user), 6.6.6.6 (proxy)"
                #   Direct calls w/o proxy: x-forwarded-for: "10.1.13.128 (user)"
                #   Spoofed: x-forwarded-for: "2.2.2.2 (spoof), 10.1.13.128 (user), 6.6.6.6 (proxy)"
                ips = value.decode("utf-8").split(",")
                ip = ips[-config.XFF_DEPTH].strip()

    return ip
