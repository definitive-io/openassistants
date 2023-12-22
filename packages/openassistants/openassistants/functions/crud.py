import abc
import asyncio
import json
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Annotated, Any, Callable, Dict, List, Optional, Tuple, Union

from langchain.chains.openai_functions.openapi import openapi_spec_to_openai_fn
from langchain_community.utilities.openapi import OpenAPISpec
from openassistants.contrib.advisor_function import AdvisorFunction
from openassistants.contrib.duckdb_query import DuckDBQueryFunction
from openassistants.contrib.langchain_ddg_tool import DuckDuckGoToolFunction
from openassistants.contrib.python_callable import PythonCallableFunction
from openassistants.contrib.python_eval import PythonEvalFunction
from openassistants.contrib.sqlalchemy_query import QueryFunction
from openassistants.contrib.text_response import TextResponseFunction
from openassistants.data_models.function_output import TextOutput
from openassistants.data_models.json_schema import JSONSchema
from openassistants.functions.base import (
    BaseFunction,
    BaseFunctionParameters,
    IBaseFunction,
)
from openassistants.utils import yaml as yaml_utils
from pydantic import Field, TypeAdapter
from starlette.concurrency import run_in_threadpool

AllFunctionTypes = Annotated[
    QueryFunction
    | DuckDBQueryFunction
    | PythonEvalFunction
    | DuckDuckGoToolFunction
    | TextResponseFunction
    | AdvisorFunction,
    Field(json_schema_extra={"discriminator": "type"}),
]


class FunctionCRUD(abc.ABC):
    @abc.abstractmethod
    def read(self, slug: str) -> Optional[IBaseFunction]:
        pass

    @abc.abstractmethod
    def list_ids(self) -> List[str]:
        pass

    async def aread(self, function_id: str) -> Optional[IBaseFunction]:
        return await run_in_threadpool(self.read, function_id)

    async def alist_ids(self) -> List[str]:
        return await run_in_threadpool(self.list_ids)

    async def aread_all(self) -> List[IBaseFunction]:
        ids = await self.alist_ids()
        return await asyncio.gather(*[self.aread(f_id) for f_id in ids])  # type: ignore


class LocalCRUD(FunctionCRUD):
    def __init__(self, library_id: str, directory: str = "library"):
        self.library_id = library_id
        self.directory = Path(directory) / library_id

    def read(self, function_id: str) -> Optional[BaseFunction]:
        try:
            if (yaml_file := self.directory / f"{function_id}.yaml").exists():
                with yaml_file.open() as f:
                    parsed_yaml = yaml_utils.load(f)
                return TypeAdapter(AllFunctionTypes).validate_python(
                    parsed_yaml | {"id": function_id}
                )  # type: ignore
            else:
                return None
        except Exception as e:
            raise RuntimeError(f"Failed to load: {function_id}") from e

    async def aread_all(self) -> List[BaseFunction]:
        ids = self.list_ids()
        return [self.read(f_id) for f_id in ids]  # type: ignore

    def list_ids(self) -> List[str]:
        return [
            file.stem for file in self.directory.iterdir() if file.suffix == ".yaml"
        ]


class PythonCRUD(FunctionCRUD):
    def __init__(self, functions: List[IBaseFunction]):
        self.functions = functions

    def read(self, slug: str) -> Optional[IBaseFunction]:
        for function in self.functions:
            if function.get_id() == slug:
                return function

        return None

    def list_ids(self) -> List[str]:
        return [function.get_id() for function in self.functions]


class OpenAPICRUD(PythonCRUD):
    openapi: OpenAPISpec

    @staticmethod
    def openai_fns_to_openapi_function(
        fns: Tuple[List[Dict[str, Any]], Callable],
    ) -> List[PythonCallableFunction]:
        openapi_functions = []
        callable_fn = fns[1]

        for function_schema in fns[0]:

            async def wrapped_fn(deps, fs=function_schema):
                response = callable_fn(fs["name"], fn_args=deps.arguments)
                if response.headers.get("Content-Type") == "application/json":
                    try:
                        response_json = response.json()
                        yield [
                            TextOutput(
                                text="```json\n"
                                + json.dumps(response_json, indent=2)
                                + "\n```"
                            )
                        ]
                    except JSONDecodeError:
                        yield [TextOutput(text=response.text)]
                else:
                    yield [TextOutput(text=response.text)]

            parameters = function_schema["parameters"]
            if "required" not in parameters:
                parameters["required"] = []

            openapi_functions.append(
                PythonCallableFunction(
                    id=function_schema["name"],
                    display_name=function_schema["name"],
                    description=function_schema["description"],
                    parameters=BaseFunctionParameters(
                        json_schema=TypeAdapter(JSONSchema).validate_python(parameters)
                    ),
                    confirm=True,
                    execute_callable=wrapped_fn,
                )
            )

        return openapi_functions

    def __init__(self, spec: Union[OpenAPISpec, str], base_url: Optional[str]):
        if isinstance(spec, str):
            self.openapi = OpenAPISpec.from_url(spec)
        else:
            self.openapi = spec

        if base_url is not None:
            if self.openapi.servers is None:
                self.openapi.servers = []
            self.openapi.servers[0].url = base_url

        openai_functions = openapi_spec_to_openai_fn(self.openapi)
        functions = OpenAPICRUD.openai_fns_to_openapi_function(openai_functions)

        super().__init__(functions)
