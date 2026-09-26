from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    Prefer X-Forwarded-For (set by reverse proxies/load balancers in front
    of the app in most real deployments) over the raw socket peer address,
    which would otherwise just be the proxy's own IP for every visitor.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # The header can be a comma-separated chain; the first entry is the
        # original client.
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
