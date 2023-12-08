from typing import List

from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.chat_models.openai import ChatOpenAI
from langchain.schema.embeddings import Embeddings
from langchain.schema import BaseStore
from langchain.embeddings import CacheBackedEmbeddings


def is_openai(chat):
    return isinstance(chat, ChatOpenAI) or isinstance(chat, AzureChatOpenAI)


class LangChainCachedEmbeddings(Embeddings):
    def __init__(
            self,
            langchain_underlying_embedder: Embeddings,
            langchain_embedding_store: BaseStore[str, bytes],
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
            namespace=namespace,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedder.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embedder.embed_query(text)
