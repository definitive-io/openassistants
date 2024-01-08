import os
from typing import Annotated

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from langchain.embeddings import OpenAIEmbeddings
from langchain.storage import RedisStore
from openassistants.contrib.advisor_function import AdvisorFunction
from openassistants.contrib.duckdb_query import DuckDBQueryFunction
from openassistants.contrib.langchain_ddg_tool import DuckDuckGoToolFunction
from openassistants.contrib.python_eval import PythonEvalFunction
from openassistants.contrib.sqlalchemy_query import QueryFunction
from openassistants.contrib.text_response import TextResponseFunction
from openassistants.core.assistant import Assistant
from openassistants.functions.base import IFunction
from openassistants.functions.crud import (
    LocalYAMLLibrary,
    OpenAPILibrary,
    PythonLibrary,
)
from openassistants.utils.langchain_util import LangChainCachedEmbeddings
from openassistants_fastapi import RouteAssistants, create_router
from pydantic import Field, TypeAdapter

from fast_api_server.find_email_by_name_function import find_email_by_name_function

app = FastAPI()


# Specify all the function types that are allowed in the local YAML library
AllFunctionTypes = Annotated[
    QueryFunction
    | DuckDBQueryFunction
    | PythonEvalFunction
    | DuckDuckGoToolFunction
    | TextResponseFunction
    | AdvisorFunction,
    Field(json_schema_extra={"discriminator": "type"}),
]


def model_parser(d: dict) -> IFunction:
    return TypeAdapter(AllFunctionTypes).validate_python(d)  # type: ignore


local_library = LocalYAMLLibrary(
    "piedpiper",
    model_parser,
    "library",
)

# create a library with the custom function
custom_python_lib = PythonLibrary(functions=[find_email_by_name_function])

openapi_lib = OpenAPILibrary(
    spec="https://petstore3.swagger.io/api/v3/openapi.json",
    base_url="https://petstore3.swagger.io/api/v3",
)

# used redis embedding cache if available
if (redis_embedding_url := os.getenv("REDIS_URL")) is not None:
    embedding_cache = RedisStore(
        redis_url=redis_embedding_url,
    )
    entity_embedding_model = LangChainCachedEmbeddings(
        langchain_underlying_embedder=OpenAIEmbeddings(),
        langchain_embedding_store=embedding_cache,
    )
else:
    entity_embedding_model = LangChainCachedEmbeddings(
        langchain_underlying_embedder=OpenAIEmbeddings(),
    )


hooli_assistant = Assistant(
    libraries=[local_library, custom_python_lib, openapi_lib],
    scope_description="""Only answer questions about Hooli company related matters.
You're also allowed to answer questions that refer to anything in the current chat history.""",  # noqa: E501
    entity_embedding_model=entity_embedding_model,
)

route_assistants = RouteAssistants(assistants={"hooli": hooli_assistant})

api_router = create_router(route_assistants)

# IMPORTANT! Do not ship this to production! You should be more restrictive
# https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router)


@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy"}
