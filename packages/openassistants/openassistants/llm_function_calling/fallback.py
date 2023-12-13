from typing import List

from langchain.chat_models.base import BaseChatModel
from langchain.schema.messages import HumanMessage, SystemMessage
from openassistants.data_models.chat_messages import OpasMessage
from openassistants.functions.utils import AsyncStreamVersion
from openassistants.llm_function_calling.utils import build_chat_history_prompt
from openassistants.utils.langchain_util import string_from_message


async def perform_general_qa(
    chat: BaseChatModel,
    user_query: str,
    chat_history: List[OpasMessage],
    scope_description: str,
) -> AsyncStreamVersion[str]:
    final_messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(
            content=f"""
{build_chat_history_prompt(chat_history)}

Try to answer the user's question based on the chat history: {user_query}.

If the user question is considered outside of the scope of the assistant, respond with "I'm sorry, I can't help you with that. Do you have any other questions?"

SCOPE DESCRIPTION START
{scope_description}
SCOPE DESCRIPTION END
"""  # noqa: E501
        ),
    ]

    full = ""
    async for response_message in chat.astream(
        final_messages,
        {"tags": ["fallback"]},
    ):
        full += string_from_message(response_message)
        yield full
