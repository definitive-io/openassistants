from typing import List

from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.chat_models.openai import ChatOpenAI
from langchain.embeddings import CacheBackedEmbeddings
from langchain.schema import BaseStore
from langchain.schema.embeddings import Embeddings
from langchain.schema.messages import BaseMessage
from langchain.storage import LocalFileStore
from langchain_core.language_models import BaseChatModel


def openai_function_call_enabled(chat: BaseChatModel):
    return (
        isinstance(chat, ChatOpenAI) or isinstance(chat, AzureChatOpenAI)
    ) and chat.model_name in {
        "gpt-4",
        "gpt-4-1106-preview",
        "gpt-4-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0613",
    }


def string_from_message(message: BaseMessage) -> str:
    if isinstance(message.content, str):
        return message.content
    else:
        raise ValueError(f"Unknown message type {type(message)}")


class LangChainCachedEmbeddings(Embeddings):
    """
    A wrapper around a langchain Embedder that caches the embeddings in a store.
    Default store is a LocalFileStore, but can be switched to Redis in a production environment.
    """  # noqa: E501

    def __init__(
        self,
        langchain_underlying_embedder: Embeddings,
        langchain_embedding_store: BaseStore[str, bytes] = LocalFileStore(
            "/tmp/openassistants_embeddings_cache"
        ),
    ):
        embedder_params = ",".join(
            sorted(
                [
                    f"{k}={v}"
                    for k, v in langchain_underlying_embedder.__dict__.items()
                    if k in ["model"]
                ]
            )
        )

        namespace = (
            f"{langchain_underlying_embedder.__class__.__name__}({embedder_params})"
        )

        self.embedder = CacheBackedEmbeddings.from_bytes_store(
            langchain_underlying_embedder,
            langchain_embedding_store,
            namespace=str(hash(namespace)),
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedder.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embedder.embed_query(text)
