async def cache_control(request, call_next):
    """
    Adds the Cache-Control header to all responses.

    Args:
        request (Request): The request object.
        call_next (Callable): The next middleware function.

    Returns:
        Response: The response object.

    """
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        return await call_next(request)

    response = await call_next(request)
    response.headers[
        "Cache-Control"
    ] = "public, max-age 86400, stale-while-revalidate 3600, stale-if-error 3600"
    return response


async def cors(request, call_next):
    """
    Adds the Cache-Control header to all responses.

    Args:
        request (Request): The request object.
        call_next (Callable): The next middleware function.

    Returns:
        Response: The response object.

    """
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        return await call_next(request)

    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
