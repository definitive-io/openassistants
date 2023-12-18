from typing import Awaitable, Callable, List, Literal, Sequence

from openassistants.data_models.function_output import FunctionOutput, TextOutput
from openassistants.functions.base import (
    BaseFunction,
    FunctionExecutionDependency,
)
from openassistants.functions.utils import AsyncStreamVersion


class IndexFunction(BaseFunction):
    type: Literal["IndexFunction"] = "IndexFunction"
    functions: Callable[[], Awaitable[List[BaseFunction]]]

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        output = ""
        for function in await self.functions():
            if function.type == "IndexFunction":
                continue
            output += f"""**{function.display_name}**
{function.description}\n\n"""
            yield [TextOutput(text=output)]
