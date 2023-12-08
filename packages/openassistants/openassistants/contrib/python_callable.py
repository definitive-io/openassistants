from typing import Callable, Sequence

from openassistants.data_models.function_input import BaseJSONSchema
from openassistants.data_models.function_output import FunctionOutput
from openassistants.functions.base import BaseFunction, FunctionExecutionDependency
from openassistants.functions.utils import AsyncStreamVersion


class PythonCallableFunction(BaseFunction):
    callable: Callable[
        [FunctionExecutionDependency], AsyncStreamVersion[Sequence[FunctionOutput]]
    ]
    parameters: BaseJSONSchema

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        async for version in self.callable(deps):
            yield version

    async def get_parameters_json_schema(self) -> dict:
        return self.parameters.json_schema
