from typing import Awaitable, Callable, Dict, Sequence

from openassistants.data_models.function_input import BaseJSONSchema
from openassistants.data_models.function_output import FunctionOutput
from openassistants.functions.base import (
    BaseFunction,
    EntityConfig,
    FunctionExecutionDependency,
)
from openassistants.functions.utils import AsyncStreamVersion


class PythonCallableFunction(BaseFunction):
    execute_callable: Callable[
        [FunctionExecutionDependency], AsyncStreamVersion[Sequence[FunctionOutput]]
    ]

    parameters: BaseJSONSchema

    get_entity_configs_callable: Callable[[], Awaitable[dict[str, EntityConfig]]]

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        async for output in self.execute_callable(deps):
            yield output

    async def get_parameters_json_schema(self) -> dict:
        return self.parameters.json_schema

    async def get_entity_configs(self) -> Dict[str, EntityConfig]:
        return await self.get_entity_configs_callable()
