from typing import Awaitable, Callable, Mapping, Sequence

from openassistants.data_models.function_output import FunctionOutput
from openassistants.functions.base import (
    BaseFunction,
    FunctionExecutionDependency,
    IEntityConfig,
)
from openassistants.functions.utils import AsyncStreamVersion


class PythonCallableFunction(BaseFunction):
    execute_callable: Callable[
        [FunctionExecutionDependency], AsyncStreamVersion[Sequence[FunctionOutput]]
    ]

    get_entity_configs_callable: Callable[[], Awaitable[Mapping[str, IEntityConfig]]]

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        async for output in self.execute_callable(deps):
            yield output

    async def get_entity_configs(self) -> Mapping[str, IEntityConfig]:
        return await self.get_entity_configs_callable()
