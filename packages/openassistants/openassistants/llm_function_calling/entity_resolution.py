import asyncio
from typing import Any, Dict, List, Tuple

from langchain.chat_models.base import BaseChatModel
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores.usearch import USearch

from openassistants.data_models.chat_messages import OpasMessage
from openassistants.functions.base import BaseFunction, Entity, EntityConfig
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


def entity_to_document(entity: Entity) -> Document:
    doc = Document(metadata=entity.model_dump(), page_content=entity.identity)

    if entity.description:
        doc.page_content += f" ({entity.description})"

    return doc


async def _get_entities(
    entity_cfg: EntityConfig,
    entity_key: str,
    preliminary_arguments: Dict[str, Any],
    embeddings: Embeddings,
) -> Tuple[str, List[Entity]]:
    documents = [entity_to_document(entity) for entity in entity_cfg.entities]

    query = str(preliminary_arguments[entity_key])

    vec_result = await _vec_search(documents, query, embeddings)

    return entity_key, [Entity(**r.metadata) for r in vec_result]


async def resolve_entities(
    function: BaseFunction,
    function_infilling_llm: BaseChatModel,
    embeddings: Embeddings,
    user_query: str,
    chat_history: List[OpasMessage],
) -> Dict[str, List[Entity]]:
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
