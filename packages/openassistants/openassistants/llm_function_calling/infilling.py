from typing import Dict, TypedDict

from langchain.schema.messages import HumanMessage

from openassistants.data_models.chat_messages import opas_to_lc
from openassistants.functions.base import BaseFunction
from openassistants.llm_function_calling.utils import generate_to_json


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

    final_messages = history_messages + [
        HumanMessage(
            content=f"""We are analyzing the following function:
{await function.get_signature()}

User query: "{user_query}"

For each of the arguments decide:
- Should the argument be used?
- Can we find the right value for the argument from the user query or from previous messages? We need to be able to derive the full correct value for the argument without any additional information.
"""  # noqa: E501
        )
    ]

    result = await generate_to_json(
        chat, final_messages, json_schema, "generate_argument_decisions"
    )

    return result


async def generate_arguments(
    function: BaseFunction, chat, user_query, chat_history
) -> dict:
    json_schema = await function.get_parameters_json_schema()

    history_messages = opas_to_lc(chat_history)[:-1]

    final_messages = history_messages + [
        HumanMessage(
            content=f"""We want to invoke the following function:
{await function.get_signature()}

Provide the arguments for the function call that match the user query in JSON.

User query: "{user_query}"
"""
        ),
    ]

    result = await generate_to_json(
        chat, final_messages, json_schema, "generate_arguments"
    )

    return result
