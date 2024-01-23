from pydantic import BaseModel, root_validator, Field


class QueryParams(BaseModel):
    """
    Represents the query parameters for the search API.

    Attributes:
        exactTerms (str): The exact terms to search for.
        fields (str): The fields to include in the search results.
        cx (str): The custom search engine ID.
        hl (str): The language code for the search results.
        lr (str): The language restriction for the search results.
        filter (int): The filter for the search results.
        safe (str): The safety level for the search results.
        num (int): The number of search results to return.
    """

    exactTerms: str
    fields: str
    cx: str
    hl: str
    lr: str
    filter: int
    safe: str
    num: int


class RequestHeaders(BaseModel):
    """
    Represents the request headers for the API.
    """

    class Config:
        extra = "allow"

    @root_validator(pre=True)
    def check_all_values_are_strings(cls, values):
        """
        Validates that all values in the request headers are strings.
        Raises a ValueError if a non-string value is found.
        """
        for key, value in values.items():
            if not isinstance(value, str):
                raise ValueError(
                    f"The value for '{key}' is not a string. Found value: {value}"
                )
        return values


class Metatags(BaseModel):
    """
    Represents the metadata tags for a search result.

    Attributes:
        id (str): The store ID of the app.
        name (str): The title of the app.
        logo (str): The URL of the app's logo image.
        url (str): The URL of the app's playstore page.
        description (str): The description of the app.
    """

    id: str = Field(..., alias="appstore:store_id", serialization_alias="id")
    name: str = Field(..., alias="og:title", serialization_alias="name")
    logo: str = Field(..., alias="og:image", serialization_alias="logo")
    url: str = Field(..., alias="og:url", serialization_alias="url")
    description: str = Field(
        ..., alias="twitter:description", serialization_alias="description"
    )


class Pagemap(BaseModel):
    """
    Represents the page map of a search result.

    Attributes:
        metatags (list[Metatags]): The list of metatags associated with the page.
    """

    metatags: list[Metatags]


class Items(BaseModel):
    """
    Represents a collection of items.
    """

    pagemap: Pagemap


class SearchResults(BaseModel):
    """
    Represents the search results returned by the API.

    Attributes:
        items (list[Items]): A list of items returned in the search results.
    """

    items: list[Items]
