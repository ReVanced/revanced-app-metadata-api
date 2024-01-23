import uvicorn
import redis.asyncio as redis
from typing import Annotated, Optional
from contextlib import asynccontextmanager

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query, status, Depends
from fastapi.responses import ORJSONResponse, StreamingResponse, RedirectResponse

from api.utils.funcs import env
from api.models.search import Metatags
from api.controllers.search import Engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    An asynchronous context manager for the lifespan of the FastAPI application.

    This function initializes and closes the FastAPILimiter, which is used for rate limiting.

    Args:
        _ (FastAPI): The FastAPI application instance. This argument is not used.

    Yields:
        None

    Raises:
        Any exceptions raised by FastAPILimiter.init() or FastAPILimiter.close().

    """
    await FastAPILimiter.init(redis.from_url(env("REDIS_URL"), encoding="utf8"))
    yield
    await FastAPILimiter.close()


app = FastAPI(
    title="Google Play Store Metadata API",
    description="Return relevant metadata from Google Play Store for a given package ID.",
    version="1.0.0",
    license_info={
        "name": "AGPLv3",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html",
    },
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

engine = Engine()


@app.get(
    "/",
    response_class=RedirectResponse,
    status_code=status.HTTP_301_MOVED_PERMANENTLY,
    dependencies=[Depends(RateLimiter(times=60, seconds=1800))],
)
async def root() -> RedirectResponse:
    """
    Redirects the root URL to the /docs endpoint.

    Returns:
        RedirectResponse: A response object that redirects to /docs.
    """
    return RedirectResponse(url="/docs", status_code=status.HTTP_301_MOVED_PERMANENTLY)


@app.get(
    "/search",
    response_model=list[Metatags],
    dependencies=[Depends(RateLimiter(times=60, seconds=1800))],
)
async def search(
    id_list: Annotated[Optional[list[str]], Query(alias="id")] = None
) -> StreamingResponse:
    """
    Performs a search using the provided list of IDs.

    Args:
        id_list (Optional[list[str]]): A list of IDs to search for. Defaults to None.

    Returns:
        StreamingResponse: A streaming response object containing the search results.

    Raises:
        HTTPException: If no IDs were provided, more than 10 IDs were provided, or an error occurred during the search.
    """
    if not id_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No IDs were provided.",
        )

    if len(id_list) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The maximum number of IDs that can be searched is 10.",
        )

    try:
        return StreamingResponse(engine.search(id_list=id_list))
    except Exception as e:
        match type(e).__name__:
            case "RuntimeError":
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)
                )
            case "ValueError":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
                )
            case "ValidationError":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
            case _:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
