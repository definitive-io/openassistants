from typing import Annotated, List, Literal, Optional

import pandas as pd
from langchain.schema.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    merge_content,
)
from pydantic import BaseModel, Field

from openassistants.data_models.function_input import FunctionCall, FunctionInputRequest
from openassistants.data_models.function_output import (
    DataFrameOutput,
    FunctionOutput,
    TextOutput,
)


class SuggestedPrompt(BaseModel):
    title: str
    prompt: str


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


def _render_df_for_llm(df: pd.DataFrame) -> str:
    return df.to_csv(index=False, date_format="iso")


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


def opas_to_lc(chat_history, skip_assistant_messages=False) -> List[BaseMessage]:
    lc_messages: List[BaseMessage] = []

    for message in chat_history:
        if isinstance(message, OpasUserMessage) and message.input_response is None:
            lc_messages.append(HumanMessage(content=message.content))
        if (
            isinstance(message, OpasAssistantMessage)
            and message.function_call is not None
        ):
            fname = message.function_call.name
            fargs = message.function_call.arguments
            lc_messages.append(
                HumanMessage(
                    content=f"""\
To answer the previous question, I called a function: {fname}({fargs})
"""
                )
            )
        if (
            isinstance(message, OpasAssistantMessage)
            and message.function_call is None
            and skip_assistant_messages is False
        ):
            lc_messages.append(AIMessage(content=message.content))
        if isinstance(message, OpasFunctionMessage):
            function_message_summary = ""
            for output in message.outputs:
                if isinstance(output, DataFrameOutput):
                    function_message_summary += f"""\
The following table answers the previous question:
{_render_df_for_llm(output.dataframe.to_pd())}
"""
                elif isinstance(output, TextOutput):
                    function_message_summary += f"""\
Insight for the previous question based on the data:
{output.text}
"""
            lc_messages.append(HumanMessage(content=function_message_summary))

    ensure_alternating(lc_messages)

    return lc_messages


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
