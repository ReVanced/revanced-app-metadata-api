import asyncio
from typing import Optional
from typing_extensions import Protocol
from app.models.search import SearchResults, Metatags


class Engine(Protocol):
    async def run(self, package_id: str) -> Optional[SearchResults]:
        ...

    async def search(self, id_list: list[str]) -> list[Metatags]:
        """
        Search for metatags based on a list of IDs.

        Args:
            id_list (list[str]): A list of IDs to search for.

        Returns:
            list[Metatags]: A list of Metatags objects containing the search results.
        """
        response = []
        for item in await asyncio.gather(*[self.run(id) for id in id_list]):
            if item:
                response.append(item.items[0].pagemap.metatags[0])
        return response
