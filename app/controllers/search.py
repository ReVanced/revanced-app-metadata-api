import httpx
import asyncio
from loguru import logger
from cashews import Cache
from datetime import timedelta
from typing import AsyncGenerator
from httpx_auth import QueryApiKey

from app.utils.funcs import env
from app.models.search import QueryParams, RequestHeaders, SearchResults


class Engine:
    """
    The Engine class is responsible for performing searches using the Google Custom Search API.

    Attributes:
        search_api_key (str): The API key for the Google Custom Search API.
        search_engine_id (str): The ID of the custom search engine.
        store_title_suffix (str): The suffix to be removed from the store title.
        api_url (httpx.URL): The URL of the Google Custom Search API.
        headers (RequestHeaders): The headers to be used in the API requests.
        client (httpx.AsyncClient): The HTTP client for making API requests.
        cache (Cache): The cache for storing search results.
    """

    search_api_key: str = env("SEARCH_API_KEY")
    search_engine_id: str = env("SEARCH_ENGINE_ID")

    store_title_suffix: str = " - Apps on Google Play"

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
    async def __search(self, package_id: str) -> str:
        """
        Perform a search for a specific package ID.

        This method sends a GET request to the Google Custom Search API with the specified package ID as the exact search term.
        The response is parsed and the relevant information is extracted and returned.

        Args:
            package_id (str): The package ID to search for.

        Returns:
            str: A string representation of the search result.

        Raises:
            RuntimeError: If the API request fails.
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

        if response.status_code != 200:
            error = f"Remote replied with: {response.status_code} {response.reason_phrase} {response.text}"
            logger.error(error)
            raise RuntimeError(error)

        if not response.json().get("items"):
            error = "No items found in response."
            logger.error(error)
            return ""

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

        return str(content.items[0].pagemap.metatags[0].model_dump())

    async def search(self, id_list: list[str]) -> AsyncGenerator[str, None]:
        """
        Perform a search for a list of package IDs.

        This method creates a list of tasks to search for each package ID in the provided list.
        The tasks are run concurrently and the results are yielded as they become available.

        Args:
            id_list (list[str]): The list of package IDs to search for.

        Returns:
            AsyncGenerator[str, None]: An asynchronous generator that yields the search results.
        """
        yield "["
        first = True
        tasks = [self.__search(package_id=package_id) for package_id in id_list]
        for future in asyncio.as_completed(tasks):
            result = await future
            if result:
                if not first:
                    yield ","
                else:
                    first = False
                yield result
        yield "]"
