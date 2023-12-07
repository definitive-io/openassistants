import logging
from typing import AsyncGenerator, TypeVar

T = TypeVar("T")

# This type is used to indicate a function that can "update" its "return" value
# over time via an async generator.
AsyncStreamVersion = AsyncGenerator[T, None]

logger = logging.getLogger(__name__)


async def last_value(src: AsyncStreamVersion) -> T:
    last = None
    try:
        async for last in src:
            pass
    except Exception as e:
        logger.exception("Error while serving request")
        raise e

    return last
