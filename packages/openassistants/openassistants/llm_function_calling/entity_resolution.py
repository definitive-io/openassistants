import asyncio
from typing import Any, Dict, List

import pandas as pd
from langchain.schema import Document
from langchain.vectorstores.usearch import USearch
from langchain.embeddings.base import Embeddings

from openassistants.functions.base import BaseFunction, BaseFunctionEntityConfig


async def _vec_search(documents: List[Document], query: str, embeddings: Embeddings,
                      ) -> List[Document]:
    search: USearch = await USearch.afrom_documents(
        embedding=embeddings,
        documents=documents,
    )
    results = await search.asimilarity_search(
        query,
        k=10,
    )
    return results


async def _get_entities(
    entity_cfg: BaseFunctionEntityConfig,
    entity_key: str,
    arg_queries: Dict[str, Any],
    embeddings: Embeddings,
) -> str:

    documents = [
        Document(
            metadata=row,
            page_content=" ".join(f"{k}={v}" for k, v in row.items()),
        )
        for row in entity_cfg.entities
    ]

    query = str(arg_queries[entity_key])

    vec_result = await _vec_search(documents, query, embeddings)

    results_df = pd.DataFrame([r.metadata for r in vec_result])

    return f"""\
'{entity_key}' entities related to '{arg_queries[entity_key]}':
{results_df.to_csv(index=False)}\
"""


async def resolve_entities(
    function: BaseFunction,
    arg_queries: Dict[str, Any],
    embeddings: Embeddings,
) -> str:
    results = await asyncio.gather(
        *[
            _get_entities(entity_cfg, param_name, arg_queries, embeddings)
            for param_name, entity_cfg in (await function.get_entity_configs()).items()
        ]
    )

    return "\n\n".join(results)
