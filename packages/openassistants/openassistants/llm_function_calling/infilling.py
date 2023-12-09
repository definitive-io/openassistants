from typing import Dict, List, TypedDict

import yaml
from langchain.schema.messages import HumanMessage

from openassistants.data_models.chat_messages import (
    OpasMessage,
    OpasUserMessage,
)
from openassistants.functions.base import BaseFunction
from openassistants.llm_function_calling.utils import generate_to_json

from langchain.chat_models.base import BaseChatModel

from openassistants.utils.history_representation import opas_to_interactions


def _build_chat_history_prompt(chat_history: List[OpasMessage]) -> str:
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

    message_yamls = []

    for interaction in interactions:
        message_yamls.append(
            yaml.dump(
                interaction.dict(
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
            )
        )

    message_yamls.append(yaml.dump({"user_prompt": last_message.content.strip()}))

    sep = "---\n"

    return f"""\
CHAT HISTORY
---
{sep.join(message_yamls)}
---
END OF CHAT HISTORY
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

    final_messages = [
        HumanMessage(
            content=f"""
{_build_chat_history_prompt(chat_history)}            
            
We are analyzing the following function:
{await function.get_signature()}

For each of the arguments decide:
- Can we find the right value for the argument from the user_prompt or from the history?
- Should the argument be used?

Respond with the JSON.
"""  # noqa: E501
        )
    ]

    result = await generate_to_json(
        chat, final_messages, json_schema, "generate_argument_decisions"
    )

    return result


async def generate_arguments(
    function: BaseFunction,
    chat: BaseChatModel,
    user_query: str,
    chat_history: List[OpasUserMessage],
    entities_info: str,
) -> dict:
    json_schema = await function.get_parameters_json_schema()

    final_messages = [
        HumanMessage(
            content=f"""
{_build_chat_history_prompt(chat_history)}            
            
We want to invoke the following function:
{await function.get_signature()}

Provide the arguments for the function call that match the user_prompt in JSON.

{entities_info}
"""
        ),
    ]

    result = await generate_to_json(
        chat, final_messages, json_schema, "generate_arguments"
    )

    return result
