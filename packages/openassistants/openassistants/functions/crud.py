import abc
import asyncio
from pathlib import Path
from typing import Annotated, List, Optional

from pydantic import Field, TypeAdapter
from starlette.concurrency import run_in_threadpool

from openassistants.contrib.duckdb_query import DuckDBQueryFunction
from openassistants.contrib.python_eval import PythonEvalFunction
from openassistants.contrib.sqlalchemy_query import QueryFunction
from openassistants.functions.base import BaseFunction
from openassistants.utils import yaml

AllFunctionTypes = Annotated[
    QueryFunction | DuckDBQueryFunction | PythonEvalFunction,
    Field(json_schema_extra={"discriminator": "type"}),
]


class FunctionCRUD(abc.ABC):
    @abc.abstractmethod
    def read(self, slug: str) -> Optional[BaseFunction]:
        pass

    @abc.abstractmethod
    def list_ids(self) -> List[str]:
        pass

    async def aread(self, function_id: str) -> Optional[BaseFunction]:
        return await run_in_threadpool(self.read, function_id)

    async def alist_ids(self) -> List[str]:
        return await run_in_threadpool(self.list_ids)

    async def aread_all(self) -> List[BaseFunction]:
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
    def __init__(self, functions: List[BaseFunction]):
        self.functions = functions

    def read(self, slug: str) -> Optional[BaseFunction]:
        for function in self.functions:
            if function.id == slug:
                return function

        return None

    def list_ids(self) -> List[str]:
        return [function.id for function in self.functions]
