from copy import deepcopy
from typing import Dict, List, TypedDict

from langchain.chat_models.base import BaseChatModel
from langchain.schema.messages import HumanMessage
from openassistants.data_models.chat_messages import OpasMessage, OpasUserMessage
from openassistants.functions.base import BaseFunction, Entity
from openassistants.llm_function_calling.utils import generate_to_json
from openassistants.utils import yaml
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
    function: BaseFunction,
    chat: BaseChatModel,
    user_query: str,
    chat_history: List[OpasMessage],
) -> ArgumentDecisionDict:
    json_schema = await generate_argument_decisions_schema(function)

    final_messages = [
        HumanMessage(
            content=f"""
{_build_chat_history_prompt(chat_history)}

We are analyzing the following function:
{await function.get_signature()}

For each of the arguments decide:
- Should the argument be used?
- Can we find the right value for the argument from the user_prompt or from CHAT HISTORY?

Respond in JSON.
"""  # noqa: E501
        )
    ]

    result = await generate_to_json(
        chat,
        final_messages,
        json_schema,
        "generate_argument_decisions",
        tags=["generate_argument_decisions"],
    )

    return result


def entity_to_json_schema_obj(entity: Entity):
    d = {"const": entity.identity}
    if entity.description is not None:
        d["description"] = entity.description
    return d


async def generate_arguments(
    function: BaseFunction,
    chat: BaseChatModel,
    user_query: str,
    chat_history: List[OpasMessage],
    entities_info: Dict[str, List[Entity]],
) -> dict:
    json_schema = deepcopy(await function.get_parameters_json_schema())

    # inject the parameter entity definitions
    for param, entities in entities_info.items():
        json_schema.setdefault("definitions", {})[param] = {
            "oneOf": [entity_to_json_schema_obj(entity) for entity in entities]
        }
        json_schema["properties"][param] |= {"$ref": f"#/definitions/{param}"}

    final_messages = [
        HumanMessage(
            content=f"""
{_build_chat_history_prompt(chat_history)}

We want to invoke the following function:
{await function.get_signature()}

Provide the arguments for the function call that match the user_prompt.

Respond in JSON.
"""
        ),
    ]

    result = await generate_to_json(
        chat,
        final_messages,
        json_schema,
        "generate_arguments",
        tags=["generate_arguments"],
    )

    return result
