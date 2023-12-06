import dataclasses
from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException
from openassistants.core.assistant import Assistant
from openassistants.data_models.chat_messages import OpasMessage
from openassistants.functions.base import BaseFunction
from openassistants.utils.async_utils import last_value
from openassistants_fastapi.utils.sse import AsyncStreamVersion, sse_json_patch
from pydantic import BaseModel, Field


@dataclasses.dataclass
class RouteAssistants:
    assistants: dict[str, Assistant]


def create_router(route_assistants: RouteAssistants) -> APIRouter:
    v1alpha_router = APIRouter(
        prefix="/v1alpha",
    )

    class ChatRequest(BaseModel):
        messages: Annotated[List[OpasMessage], Field(min_items=1)]
        stream: bool = False
        autorun: Annotated[
            bool, Field(description="automatically run identified function")
        ] = True
        force_select_function: Optional[str] = None

    class ChatResponse(BaseModel):
        messages: Annotated[List[OpasMessage], Field(min_items=1)]

    @v1alpha_router.post("/assistants/{assistant_id}/chat")
    async def chat(
        assistant_id: str,
        body: ChatRequest,
    ):
        if assistant_id not in route_assistants.assistants:
            raise HTTPException(status_code=404, detail="assistant not found")

        assistant = route_assistants.assistants[assistant_id]

        async def stream() -> AsyncStreamVersion[ChatResponse]:
            async for version in assistant.run_chat(
                body.messages, body.autorun, body.force_select_function
            ):
                yield ChatResponse(messages=version)

        if body.stream:
            return sse_json_patch(stream())
        else:
            return await last_value(stream())

    @v1alpha_router.get("/libraries/{assistant_id}/functions")
    async def get_assistant_functions(
        assistant_id: str,
    ) -> List[BaseFunction]:
        if assistant_id not in route_assistants.assistants:
            raise HTTPException(status_code=404, detail="assistant not found")

        return await route_assistants.assistants[assistant_id].get_all_functions()

    @v1alpha_router.get("/libraries/{assistant_id}/functions/{function_id}")
    async def get_function_from_assistant(
        assistant_id: str,
        function_id: str,
    ) -> BaseFunction:
        if assistant_id not in route_assistants.assistants:
            raise HTTPException(status_code=404, detail="assistant not found")
        function_libraries = route_assistants.assistants[
            assistant_id
        ].function_libraries

        for library in function_libraries:
            if (func := await library.aread(function_id)) is not None:
                return func

        raise HTTPException(status_code=404, detail="function not found")

    return v1alpha_router
