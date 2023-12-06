import json
from typing import Dict, TypedDict

from langchain.schema.messages import HumanMessage, SystemMessage
from openassistants.data_models.chat_messages import opas_to_lc
from openassistants.functions.base import BaseFunction
from openassistants.llm_function_calling.utils import generate_to_json

OUTPUT_FORMAT_INSTRUCTION = """The output should be formatted as a JSON instance that conforms to the JSON schema below. 

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}

the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

{schema}

Always return a valid JSON object instance.
"""


async def generate_argument_decisions_schema(function: BaseFunction):
    # Start with the base schema
    json_schema = await function.get_parameters_json_schema()

    properties = {
        key: {"$ref": "#/definitions/nestedObject"}
        for key in json_schema["properties"].keys()
    }

    argument_decision_json_schema = {
        "type": "object",
        "properties": properties,
        "required": list(json_schema["properties"].keys()),
        "additionalProperties": False,
        "definitions": {
            "nestedObject": {
                "type": "object",
                "properties": {
                    "needed": {"type": "boolean"},
                    "can_be_found": {"type": "boolean"},
                },
                "required": ["needed", "can_be_found"],
                "additionalProperties": False,
            }
        },
    }

    return argument_decision_json_schema


class NestedObject(TypedDict):
    needed: bool
    can_be_found: bool


ArgumentDecisionDict = Dict[str, NestedObject]


async def generate_argument_decisions(
    function: BaseFunction, chat, user_query, chat_history
) -> ArgumentDecisionDict:
    json_schema = await generate_argument_decisions_schema(function)

    history_messages = opas_to_lc(chat_history)[:-1]
    final_messages = (
        [
            SystemMessage(
                content=OUTPUT_FORMAT_INSTRUCTION.format(
                    schema=json.dumps(json_schema, indent=4)
                )
            )
        ]
        + history_messages
        + [
            HumanMessage(
                content=f"""We are analyzing the following function:
{await function.get_signature()}

User query: "{user_query}"

For each of the arguments decide:
- Should the argument be used?
- Can we find the right value for the argument from the user query or from previous messages?
"""
            )
        ]
    )

    result = await generate_to_json(chat, final_messages)

    return result


async def generate_arguments(
    function: BaseFunction, chat, user_query, chat_history
) -> dict:
    json_schema = await function.get_parameters_json_schema()

    history_messages = opas_to_lc(chat_history)[:-1]

    final_messages = (
        [
            SystemMessage(
                content=OUTPUT_FORMAT_INSTRUCTION.format(
                    schema=json.dumps(json_schema, indent=4)
                )
            )
        ]
        + history_messages
        + [
            HumanMessage(
                content=f"""We want to invoke the following function:
{await function.get_signature()}

Provide the arguments for the function call that match the user query in JSON.

User query: "{user_query}"
"""
            ),
        ]
    )

    result = await generate_to_json(chat, final_messages)

    return result
