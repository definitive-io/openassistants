from typing import Awaitable, Callable, List, Literal, Sequence

from openassistants.data_models.function_output import FunctionOutput, TextOutput
from openassistants.functions.base import (
    BaseFunction,
    FunctionExecutionDependency,
    IBaseFunction,
)
from openassistants.functions.utils import AsyncStreamVersion


class IndexFunction(BaseFunction):
    type: Literal["IndexFunction"] = "IndexFunction"
    functions: Callable[[], Awaitable[List[IBaseFunction]]]

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        output = ""
        for function in await self.functions():
            if function.get_type() == "IndexFunction":
                continue
            output += f"""**{function.get_display_name()}**
{function.get_description()}\n\n"""
            yield [TextOutput(text=output)]
