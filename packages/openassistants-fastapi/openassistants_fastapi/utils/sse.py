import inspect
import logging
from typing import Any, Dict, Optional

import jsonpatch  # type: ignore
from fastapi.encoders import jsonable_encoder
from openassistants.utils.async_utils import AsyncStreamVersion
from pydantic import BaseModel
from sse_starlette import EventSourceResponse, ServerSentEvent

logger = logging.getLogger(__name__)


class _SSEJSONPatch(BaseModel):
    patch: Optional[Any] = None
    error: Optional[Any] = None


async def _patch_iter(src: AsyncStreamVersion) -> AsyncStreamVersion[str]:
    if not inspect.isasyncgen(src):
        raise TypeError("src must be an async generator")
    num_sent = 0
    old_dict: Dict[str, Any] = {}
    try:
        async for new in src:
            new_dict = jsonable_encoder(new)
            patch = jsonpatch.JsonPatch.from_diff(old_dict, new_dict)
            old_dict = new_dict
            yield _SSEJSONPatch(patch=patch.patch).json()
            num_sent += 1
    except Exception as e:
        logger.exception("Error while streaming response")
        yield _SSEJSONPatch(error=dict(code=None, detail=str(e))).json()
    finally:
        logger.info(f"closing SSE JSON Patch stream. Sent {num_sent} messages.")


def sse_json_patch(
    src: AsyncStreamVersion,
) -> EventSourceResponse:
    return EventSourceResponse(
        content=_patch_iter(src),
        ping_message_factory=lambda: ServerSentEvent(),
    )
