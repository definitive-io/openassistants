import inspect
from typing import Any, Callable, Dict, List, Literal, Sequence

from openassistants.data_models.function_output import FunctionOutput
from openassistants.functions.base import (
    BaseFunction,
    FunctionExecutionDependency,
)
from openassistants.functions.utils import AsyncStreamVersion
from pydantic import TypeAdapter


class PythonEvalFunction(BaseFunction):
    type: Literal["PythonEvalFunction"] = "PythonEvalFunction"
    python_code: str

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        # This is unsafe, make sure you trust python_code provided in the YAML
        exec_locals: Dict[str, Any] = {}

        exec(self.python_code, {}, exec_locals)

        main_func: Callable[[dict], AsyncStreamVersion[List[dict]]] = exec_locals.get(
            "main", None
        )

        if main_func is None:
            raise ValueError(f"No main function defined for action function: {self.id}")

        if not inspect.isasyncgenfunction(main_func):
            raise ValueError(
                f"Main function for action function {self.id} is not an async generator"
            )

        try:
            async for output in main_func(deps.arguments):
                parsed_output: List[FunctionOutput] = TypeAdapter(
                    List[FunctionOutput]
                ).validate_python(output)
                yield parsed_output

        except Exception as e:
            raise RuntimeError(
                f"Error while executing action function {self.id}. function raised: {e}"
            ) from e
