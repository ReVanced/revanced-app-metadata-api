from os import environ
from loguru import logger


def env(env_var: str) -> str:
    """
    Retrieves the value of the specified environment variable.

    Args:
        env_var (str): The name of the environment variable.

    Returns:
        str: The value of the environment variable.

    Raises:
        ValueError: If the environment variable is not set.
    """
    value = environ.get(env_var)
    if not value:
        logger.error(ValueError(f"No {env_var} environment variable set"))
        exit(1)
    return value
