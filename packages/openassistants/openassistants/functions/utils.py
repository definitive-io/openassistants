from typing import AsyncGenerator, TypeVar

T = TypeVar("T")

# This type is used to indicate a function that can "update" its "return"
# value over time via an async generator.
AsyncStreamVersion = AsyncGenerator[T, None]
