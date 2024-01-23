import httpx
from loguru import logger
from cashews import Cache
from typing import Optional
from datetime import timedelta
from httpx_auth import QueryApiKey

from app.interfaces.Engine import Engine

from app.utils.funcs import env
from app.models.search import QueryParams, RequestHeaders, SearchResults


class GoogleCSE(Engine):
    """
    Google Custom Search Engine (CSE) class for searching metatags based on a list of IDs.
    """

    search_api_key = env("SEARCH_API_KEY")
    search_engine_id = env("SEARCH_ENGINE_ID")

    store_title_suffix = " - Apps on Google Play"

    api_url = httpx.URL("https://customsearch.googleapis.com/customsearch/v1/?key=")

    headers = RequestHeaders(
        **{
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
        }
    )

    client = httpx.AsyncClient(http2=True)
    cache = Cache()
    cache.setup(
        env("REDIS_URL"),
        db=1,
        client_side=True,
        client_side_prefix="cache:",
        pickle_type="dill",
    )

    @cache(
        ttl=timedelta(hours=12),
        key="package_id:{package_id}",
    )
    async def run(self, package_id: str) -> Optional[SearchResults]:
        """
        Sarch for metatags based on a package ID using Google CSE.

        Args:
            package_id (str): The package ID to search for.

        Returns:
            Optional[SearchResults]: The search results as a SearchResults object, or None if no results found.
        """
        params = QueryParams(
            exactTerms=package_id,
            fields="items/pagemap/metatags(appstore:store_id,og:title,og:image,og:url,twitter:description)",
            cx=self.search_engine_id,
            hl="en",
            lr="lang_en",
            filter=1,
            safe="active",
            num=1,
        )

        response = await self.client.get(
            url=self.api_url,
            auth=QueryApiKey(api_key=self.search_api_key, query_parameter_name="key"),
            params=params.model_dump(),
            headers=self.headers.model_dump(),
        )

        if response.status_code != 200 or not response.json().get("items"):
            return None

        try:
            content = SearchResults(**response.json())
        except Exception as e:
            logger.error(e)
            raise

        content.items[0].pagemap.metatags[0].name = (
            content.items[0]
            .pagemap.metatags[0]
            .name.replace(self.store_title_suffix, "")
        )

        return content
