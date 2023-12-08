import asyncio
from typing import List, Optional

from langchain.chat_models.base import BaseChatModel
from langchain.schema.messages import HumanMessage
from pydantic import BaseModel

from openassistants.functions.base import BaseFunction
from openassistants.llm_function_calling.utils import (
    chunk_list_by_max_size,
    generate_to_json,
)


async def filter_functions(
    chat: BaseChatModel, functions: List[BaseFunction], user_query: str
) -> Optional[str]:
    functions_text = "\n".join(
        await asyncio.gather(*[f.get_signature() for f in functions])
    )
    json_schema = {
        "type": "object",
        "properties": {"function_name": {"type": "string"}},
        "required": ["function_name"],
    }
    messages = [
        HumanMessage(
            content=f"""{functions_text}
Which of these functions is most suitable given the user query: "{user_query}"?"""
        ),
    ]

    function_names = (
        await generate_to_json(chat, messages, json_schema, "filter_functions")
    ).get("function_name")

    return function_names


class SelectFunctionResult(BaseModel):
    function: Optional[BaseFunction] = None
    suggested_functions: Optional[List[BaseFunction]] = None


async def select_function(
    chat: BaseChatModel,
    functions: List[BaseFunction],
    user_query: str,
    chunk_size: int = 4,
) -> SelectFunctionResult:
    subsets = chunk_list_by_max_size(functions, chunk_size)

    # Make LLM calls in parallel
    tasks = [
        asyncio.create_task(filter_functions(chat, subset, user_query))
        for subset in subsets
    ]
    results = await asyncio.gather(*tasks)
    function_names: set[str] = set(filter(None, results))

    # Ensure the selected function names are in the loaded signatures
    selected_functions = [
        f for f in functions if f.get_function_name() in function_names
    ]
    if not selected_functions:
        return SelectFunctionResult()

    # Include the signatures of all the selected functions in the final evaluation
    selected_functions_signatures = "\n".join(
        [await f.get_signature() for f in selected_functions]
    )

    json_schema = {
        "type": "object",
        "properties": {
            "function_name": {"type": "string"},
            "suggested_function_names": {"type": "array", "items": {"type": "string"}},
        },
        "anyOf": [
            {"required": ["function_name"]},
            {"required": ["suggested_function_names"]},
        ],
    }

    selection_messages = [
        HumanMessage(
            content=f"""Prior selection reduced the candidates to these functions:
{selected_functions_signatures}

Scenario 1: There is a function in the list of candidates that is a match to the user query.
Action: provide the name of the function as the 'function_name' argument.

Scenario 2: None of the functions in the list of candidates match the user query.
Action: select related functions from the list of candidates as the 'suggested_function_names' argument. You are also allowed to return an empty list of suggested functions if you think none of the functions are a good match.

First decide which of the two scenarios is the case. Then take the appropriate action.

Given the user query: "{user_query}", which of these functions is the best match?"""  # noqa: E501
        ),
    ]

    json_result = await generate_to_json(
        chat, selection_messages, json_schema, "select_function"
    )

    function_name = json_result.get("function_name")
    suggested_function_names = json_result.get("suggested_function_names", [])

    selected_function = next(
        (f for f in selected_functions if f.get_function_name() == function_name), None
    )
    suggested_functions = [
        f
        for f in selected_functions
        if f.get_function_name() in suggested_function_names
    ] or None

    return SelectFunctionResult(
        function=selected_function, suggested_functions=suggested_functions
    )
