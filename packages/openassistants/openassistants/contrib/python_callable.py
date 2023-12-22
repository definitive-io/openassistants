from typing import Awaitable, Callable, Literal, Mapping, Optional, Sequence

from openassistants.data_models.function_output import FunctionOutput
from openassistants.functions.base import (
    BaseFunction,
    FunctionExecutionDependency,
    IEntityConfig,
)
from openassistants.functions.utils import AsyncStreamVersion


class PythonCallableFunction(BaseFunction):
    type: Literal["PythonCallableFunction"] = "PythonCallableFunction"
    execute_callable: Callable[
        [FunctionExecutionDependency], AsyncStreamVersion[Sequence[FunctionOutput]]
    ]

    get_entity_configs_callable: Optional[
        Callable[[], Awaitable[Mapping[str, IEntityConfig]]]
    ] = None

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        async for output in self.execute_callable(deps):
            yield output

    async def get_entity_configs(self) -> Mapping[str, IEntityConfig]:
        if self.get_entity_configs_callable is None:
            return {}
        return await self.get_entity_configs_callable()
