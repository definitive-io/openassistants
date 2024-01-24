import asyncio
from typing import List, Optional

from langchain.chat_models.base import BaseChatModel
from langchain.schema.messages import HumanMessage
from openassistants.functions.base import IFunction
from openassistants.llm_function_calling.utils import (
    chunk_list_by_max_size,
    generate_to_json,
)
from pydantic import BaseModel, InstanceOf


async def filter_functions(
    chat: BaseChatModel, functions: List[IFunction], user_query: str
) -> Optional[str]:
    functions_text = "\n".join([f.get_signature() for f in functions])
    json_schema = {
        "type": "object",
        "properties": {"function_name": {"$ref": "#/definitions/functions"}},
        "required": ["function_name"],
        "definitions": {
            "functions": {
                "enum": [f.get_id() for f in functions],
            }
        },
    }
    messages = [
        HumanMessage(
            content=f"""{functions_text}
Which of these functions is most suitable given the user query: "{user_query}"?

Respond in JSON.
"""
        ),
    ]

    function_names = (
        await generate_to_json(
            chat,
            messages,
            json_schema,
            "filter_functions",
            tags=["select_function_pre"],
        )
    ).get("function_name")

    return function_names


class SelectFunctionResult(BaseModel):
    function: Optional[InstanceOf[IFunction]] = None
    suggested_functions: Optional[List[InstanceOf[IFunction]]] = None


async def select_function(
    chat: BaseChatModel,
    functions: List[IFunction],
    user_query: str,
    chunk_size: int = 4,
) -> SelectFunctionResult:
    non_fallbacks = [f for f in functions if not f.get_is_fallback()]
    fallbacks = [f for f in functions if f.get_is_fallback()]

    subsets = chunk_list_by_max_size(non_fallbacks, chunk_size)

    # Make LLM calls in parallel
    tasks = [
        asyncio.create_task(filter_functions(chat, subset, user_query))
        for subset in subsets
    ]
    results = await asyncio.gather(*tasks)
    function_names: set[str] = set(filter(None, results))

    # Ensure the selected function names are in the loaded signatures
    selected_functions = [f for f in functions if f.get_id() in function_names]

    if len(selected_functions) == 0 and len(fallbacks) == 0:
        return SelectFunctionResult()

    # Include the signatures of all the selected functions in the final evaluation
    selected_functions_signatures = "\n".join(
        [f.get_signature() for f in selected_functions]
    )

    json_schema = {
        "type": "object",
        "properties": {
            "reason": {"type": "string"},
            "function_name": {"$ref": "#/definitions/functions"},
            "related_function_names": {
                "type": "array",
                "items": {"$ref": "#/definitions/functions"},
            },
        },
        "definitions": {
            "functions": {
                "enum": [f.get_id() for f in selected_functions + fallbacks],
            }
        },
    }

    fallbacks_signatures = "\n".join([f.get_signature() for f in fallbacks])

    selection_messages = [
        HumanMessage(
            content=f"""\
Prior selection reduced the candidates to these functions:

{selected_functions_signatures}

These fallback functions can be used when none of the above functions are a good match:

{fallbacks_signatures}

Scenario 1: There is a function in the list of candidates that is a match to the user query.
Action: provide the name of the function as the 'function_name' argument.

Scenario 2: None of the functions in the list of candidates match the user query.
Action: select related functions from the list of candidates as the 'related_function_names' argument.
You are also allowed to return an empty list of related functions if you think none of the functions are a good match.

First decide which of the two scenarios is the case. Then take the appropriate action.

Given the user query: "{user_query}", which of these functions is the best match?

Respond in JSON.
"""  # noqa: E501
        ),
    ]

    json_result = await generate_to_json(
        chat,
        selection_messages,
        json_schema,
        "select_function",
        tags=["select_function"],
    )

    function_name = json_result.get("function_name")
    suggested_function_names = json_result.get("related_function_names", [])

    selected_function = next(
        (f for f in selected_functions + fallbacks if f.get_id() == function_name), None
    )
    suggested_functions = [
        f
        for f in selected_functions + fallbacks
        if f.get_id() in suggested_function_names
    ] or None

    return SelectFunctionResult(
        function=selected_function,
        suggested_functions=suggested_functions,
    )
