import asyncio
from typing import Any, Dict, List, Tuple

from langchain.chat_models.base import BaseChatModel
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores.usearch import USearch
from openassistants.data_models.chat_messages import OpasMessage
from openassistants.functions.base import (
    IBaseFunction,
    IEntity,
    IEntityConfig,
)
from openassistants.llm_function_calling.infilling import generate_arguments


async def _vec_search(
    documents: List[Document],
    query: str,
    embeddings: Embeddings,
) -> List[Document]:
    search: USearch = await USearch.afrom_documents(
        embedding=embeddings,
        documents=documents,
    )
    results = await search.asimilarity_search(
        query,
        k=3,
    )
    return results


def entity_to_document(entity: IEntity) -> Document:
    doc = Document(
        metadata=dict(id=entity.get_identity()), page_content=entity.get_identity()
    )

    if entity.get_description:
        doc.page_content += f" ({entity.get_description})"

    return doc


async def _get_entities(
    entity_cfg: IEntityConfig,
    entity_key: str,
    preliminary_arguments: Dict[str, Any],
    embeddings: Embeddings,
) -> Tuple[str, List[IEntity]]:
    documents = [entity_to_document(entity) for entity in entity_cfg.get_entities()]

    query = str(preliminary_arguments[entity_key])

    vec_result = await _vec_search(documents, query, embeddings)

    # filter for entities that in vec result
    ids: set[str] = set([doc.metadata["id"] for doc in vec_result])

    entities = [
        entity for entity in entity_cfg.get_entities() if entity.get_identity() in ids
    ]

    return entity_key, entities


async def resolve_entities(
    function: IBaseFunction,
    function_infilling_llm: BaseChatModel,
    embeddings: Embeddings,
    user_query: str,
    chat_history: List[OpasMessage],
) -> Dict[str, List[IEntity]]:
    entity_configs = await function.get_entity_configs()

    # skip if no entity configs
    if len(entity_configs) == 0:
        return {}

    preliminary_arguments = await generate_arguments(
        function,
        function_infilling_llm,
        user_query,
        chat_history,
        {},
    )

    results = await asyncio.gather(
        *[
            _get_entities(entity_cfg, param_name, preliminary_arguments, embeddings)
            for param_name, entity_cfg in entity_configs.items()
        ]
    )

    return {key: entities for key, entities in results}
