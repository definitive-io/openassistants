import abc
import asyncio
from pathlib import Path
from typing import Annotated, List, Optional

from openassistants.contrib.advisor_function import AdvisorFunction
from openassistants.contrib.duckdb_query import DuckDBQueryFunction
from openassistants.contrib.langchain_ddg_tool import DuckDuckGoToolFunction
from openassistants.contrib.python_eval import PythonEvalFunction
from openassistants.contrib.sqlalchemy_query import QueryFunction
from openassistants.contrib.text_response import TextResponseFunction
from openassistants.functions.base import BaseFunction, IBaseFunction
from openassistants.utils import yaml
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
                    parsed_yaml = yaml.load(f)
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
            file.stem
            for file in self.directory.iterdir()
            if file.suffix == ".yaml" or file.suffix == ".py"
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
