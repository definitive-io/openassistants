from typing import Annotated, List, Literal, Optional

from langchain.schema.messages import BaseMessage, merge_content
from openassistants.data_models.function_input import FunctionCall, FunctionInputRequest
from openassistants.data_models.function_output import FunctionOutput
from pydantic import BaseModel, Field


class OpasUserMessage(BaseModel):
    role: Literal["user"] = "user"
    content: str
    input_response: Optional[FunctionCall] = Field(
        default=None,
        description="the user's response to an input request. "
        "must satisfy the schema in the assistants input request",
    )


class OpasAssistantMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: Annotated[str, Field(description="stuff like rejection messages go here")]
    input_request: Optional[FunctionInputRequest] = Field(
        description="a widget should be shown to the user when this is present",
        default=None,
    )
    function_call: Optional[FunctionCall] = Field(
        description="informs the client a function call is happening "
        "with certain parameters. may be shown to the user",
        default=None,
    )


class OpasFunctionMessage(BaseModel):
    role: Literal["function"] = "function"
    name: str
    outputs: Annotated[
        List[FunctionOutput],
        Field(
            description="the outputs of the function. "
            "can only be certain types so the client knows how to display it"
        ),
    ]


OpasMessage = Annotated[
    OpasUserMessage | OpasAssistantMessage | OpasFunctionMessage,
    Field(json_schema_extra={"descriminator": "role"}),
]


def ensure_alternating(chat_history: List[BaseMessage]) -> List[BaseMessage]:
    """
    Ensure that the chat history alternates between user and assistant messages.
    If theres a repeated role, concatenate the messages.
    """

    fixed: List[BaseMessage] = []

    message: BaseMessage
    for i, message in enumerate(chat_history):
        if i == 0:
            fixed.append(message)
        elif message.type == fixed[-1].type:
            fixed[-1].content = merge_content(fixed[-1].content, message.content)
        else:
            fixed.append(message)

    return fixed
