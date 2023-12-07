from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.chat_models.openai import ChatOpenAI


def is_openai(chat):
    return isinstance(chat, ChatOpenAI) or isinstance(chat, AzureChatOpenAI)
