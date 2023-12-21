import dataclasses
from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException
from openassistants.core.assistant import Assistant
from openassistants.data_models.chat_messages import OpasMessage
from openassistants.utils.async_utils import last_value
from pydantic import BaseModel, Field
from sse_starlette import EventSourceResponse

from openassistants_fastapi.utils.sse import AsyncStreamVersion, sse_json_patch


class ChatRequest(BaseModel):
    messages: Annotated[List[OpasMessage], Field(min_items=1)]
    stream: bool = False
    autorun: Annotated[
        bool, Field(description="automatically run identified function")
    ] = True
    force_select_function: Optional[str] = None


class ChatResponse(BaseModel):
    messages: Annotated[List[OpasMessage], Field(min_items=1)]


@dataclasses.dataclass
class RouteAssistants:
    assistants: dict[str, Assistant]


async def chat_handler(
    assistant: Assistant,
    body: ChatRequest,
) -> EventSourceResponse | ChatResponse:
    async def stream() -> AsyncStreamVersion[ChatResponse]:
        async for version in assistant.run_chat(
            body.messages, body.autorun, body.force_select_function
        ):
            yield ChatResponse(messages=version)

    if body.stream:
        return sse_json_patch(stream())
    else:
        return await last_value(stream())


def create_router(route_assistants: RouteAssistants) -> APIRouter:
    v1alpha_router = APIRouter(
        prefix="/v1alpha",
    )

    @v1alpha_router.post("/assistants/{assistant_id}/chat")
    async def chat(
        assistant_id: str,
        body: ChatRequest,
    ):
        if assistant_id not in route_assistants.assistants:
            raise HTTPException(status_code=404, detail="assistant not found")

        assistant = route_assistants.assistants[assistant_id]

        return await chat_handler(assistant, body)

    return v1alpha_router
