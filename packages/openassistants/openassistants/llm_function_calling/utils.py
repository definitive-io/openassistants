import json
from typing import Optional

import numpy as np
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models.openai import ChatOpenAI
from langchain.schema.messages import SystemMessage

from openassistants.data_models.chat_messages import ensure_alternating

OUTPUT_FORMAT_INSTRUCTION = """\
The output should fit the JSON Schema:

{schema}

Always return valid JSON.
"""  # noqa: E501


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
) -> dict:
    return await generate_to_json_generic(chat, messages, output_json_schema)


async def generate_to_json_generic(
    chat,
    messages,
    output_json_schema: Optional[dict],
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
    response = await chat.ainvoke(ensure_alternating(messages))
    content = response.content

    print("RESPONSE CONTENT:", content)

    json_substring = find_json_substring(content)
    if json_substring is not None:
        try:
            output_message = json.loads(json_substring)
            return output_message
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e, "\nResponse content:", content)
            return {}
    else:
        print("No JSON content found in response.")
        return {}


async def generate_to_json_openai(
    chat: ChatOpenAI, messages, output_json_schema: dict, task_name: str
) -> dict:
    system_message = SystemMessage(content="You are a helpful assistant.")
    messages = [system_message] + messages
    messages = ensure_alternating(messages)

    response = await chat.ainvoke(
        messages,
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

    print("LLM RESPONSE:", response)

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
