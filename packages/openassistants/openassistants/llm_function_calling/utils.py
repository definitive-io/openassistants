import json

import numpy as np
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models.openai import ChatOpenAI
from langchain.schema.messages import SystemMessage

from openassistants.data_models.chat_messages import ensure_alternating
from openassistants.utils.langchain import is_openai

OUTPUT_FORMAT_INSTRUCTION = """\
The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}

the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

{schema}

Always return a valid JSON object instance.
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
    chat: BaseChatModel, messages, output_json_schema, task_name: str
) -> dict:
    if is_openai(chat):
        assert isinstance(chat, ChatOpenAI)
        return await generate_to_json_openai(
            chat, messages, output_json_schema, task_name
        )
    else:
        return await generate_to_json_generic(chat, messages, output_json_schema)


async def generate_to_json_generic(chat, messages, output_json_schema) -> dict:
    system_message = SystemMessage(
        content=OUTPUT_FORMAT_INSTRUCTION.format(
            schema=json.dumps(output_json_schema, indent=4)
        )
    )

    messages = [system_message] + messages
    response = await chat.ainvoke(ensure_alternating(messages))
    content = response.content

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
                "description": "Get the current weather in a given location",
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
