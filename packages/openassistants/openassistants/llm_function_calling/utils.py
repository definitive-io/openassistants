import json
from typing import List, Optional

import numpy as np
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models.openai import ChatOpenAI
from langchain.schema.messages import BaseMessage, SystemMessage
from openassistants.data_models.chat_messages import (
    OpasMessage,
    OpasUserMessage,
    ensure_alternating,
)
from openassistants.utils import yaml
from openassistants.utils.history_representation import opas_to_interactions
from openassistants.utils.langchain_util import openai_function_call_enabled

OUTPUT_FORMAT_INSTRUCTION = """\
You are a helpful assistant.

Your responses MUST be formatted as a valid JSON instance that conforms to the JSON schema below.

{schema}
"""  # noqa: E501


def build_chat_history_prompt(chat_history: List[OpasMessage]) -> str:
    """
    Build a string that looks like

    CHAT HISTORY
    ---
    user_prompt: ...
    function_name: ...
    function_arguments: ...
    function_output_data: ...
    ---
    user: ...
    ---
    END OF CHAT HISTORY
    """

    previous_history, last_message = chat_history[:-1], chat_history[-1]

    assert isinstance(last_message, OpasUserMessage)

    interactions = opas_to_interactions(previous_history)

    interactions_dicts = [
        interaction.model_dump(
            mode="json",
            include={
                "user_prompt",
                "assistant_response",
                "function_name",
                "function_arguments",
                "function_output_data",
                "function_output_summary",
            },
            exclude_none=True,
        )
        for interaction in interactions
    ] + [{"user_prompt": last_message.content.strip()}]

    message_yaml_str = yaml.dumps_all(interactions_dicts)

    return f"""\
CHAT HISTORY
---
{message_yaml_str.strip()}
---
END OF CHAT HISTORY
"""


def chunk_list_by_max_size(lst, max_size):
    n = (len(lst) + max_size - 1) // max_size
    return [chunk.tolist() for chunk in np.array_split(lst, n)]


def find_json_substring(s):
    start = s.find("{")
    end = s.rfind("}") + 1
    if start != -1 and end != -1:
        return s[start:end]
    return None


async def generate_to_json(
    chat: BaseChatModel,
    messages,
    output_json_schema: Optional[dict],
    task_name: str,
    tags: Optional[list[str]] = None,
) -> dict:
    if output_json_schema is not None and openai_function_call_enabled(chat):
        assert isinstance(chat, ChatOpenAI)
        return await generate_to_json_openai(
            chat, messages, output_json_schema, task_name, tags or []
        )
    else:
        return await generate_to_json_generic(
            chat, messages, output_json_schema, tags or []
        )


async def generate_to_json_generic(
    chat,
    messages: list[BaseMessage],
    output_json_schema: Optional[dict],
    tags: list[str],
) -> dict:
    if output_json_schema is not None:
        system_message = SystemMessage(
            content=OUTPUT_FORMAT_INSTRUCTION.format(
                schema=json.dumps(output_json_schema, indent=4)
            )
        )
    else:
        system_message = SystemMessage(
            content="You are a helpful assistant. You will respond in JSON"
        )

    messages = [system_message] + messages
    response = await chat.ainvoke(ensure_alternating(messages), {"tags": tags})
    content = response.content

    json_substring = find_json_substring(content)
    if json_substring is not None:
        try:
            output_message = json.loads(json_substring)
            return output_message
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to decode JSON: {e}\nResponse content: {content}"
            ) from e
    else:
        raise ValueError(
            f"Could not find JSON substring in response content: {content}"
        )


async def generate_to_json_openai(
    chat: ChatOpenAI,
    messages: list[BaseMessage],
    output_json_schema: dict,
    task_name: str,
    tags: list[str],
) -> dict:
    system_message = SystemMessage(content="You are a helpful assistant.")
    messages = [system_message] + messages
    messages = ensure_alternating(messages)

    response = await chat.ainvoke(
        messages,
        {"tags": tags},
        functions=[
            {
                "type": "function",
                "name": task_name,
                "description": task_name,
                "parameters": output_json_schema,
            }
        ],
        function_call={"name": task_name},
    )

    if "function_call" in response.additional_kwargs:
        function_call = response.additional_kwargs["function_call"]

        # Check if function_call['name'] matches the task_name
        if function_call["name"] != task_name:
            raise ValueError(
                f"Function call name {function_call['name']} "
                f"does not match task name {task_name}"
            )

        # Return function_call['arguments'] as parsed dict
        try:
            return json.loads(function_call["arguments"])
        except json.JSONDecodeError as e:
            raise e

    raise ValueError("No function call in response")
