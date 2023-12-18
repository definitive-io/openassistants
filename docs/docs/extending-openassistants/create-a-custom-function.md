---
sidebar_position: 1
---

# Create a custom function

You can create your own custom functions in OpenAssistants by extending the base class `BaseFunction`.

Let's take a look at the included `PythonEvalFunction` to get a sense of how this works.

The following Python function:

```python

class PythonEvalFunction(BaseFunction):
    type: Literal["PythonEvalFunction"] = "PythonEvalFunction"
    parameters: BaseJSONSchema
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

    async def get_parameters_json_schema(self) -> dict:
        return self.parameters.json_schema
```

Note the following:

- Your class must have an `execute` function which runs asyncronously, which means it must be prepended with `async` where results are `yielded`, not `returned`
- `AsyncStreamVersion[Sequence[FunctionOutput]]`: this means that the `execute` function yields a list of `FunctionOutput` type. `FunctionOutput` is a generic type that encompasses `TextOutput`, `DataFrameOutput`, `VisualizationOutput` and `FollowUpsOutput`. Since it's a sequence, you can return more than one type in the same query response (i.e. return a table via `DataFrameOutput` and then a visualization of the data via `VisualizationOutput` in the same chat response). Note the output of function `main` in the yaml definition below for proper formatting

Is used in a YAML function definition as follows:

```yaml
name: send_purchase_inquiry_email
display_name: Send purchase inquiry email
description: |
  send an inquiry email about a recent purchase to an employee
sample_questions:
  - send purchase inquiry email
parameters:
  json_schema:
    type: object
    properties:
      to:
        type: string
        format: email
        description: email address to send to
    required:
      - to
type: PythonEvalFunction
python_code: |
  async def main(args: dict):
    import asyncio
    yield [{"type": "text", "text": "Sending email..."}]
    await asyncio.sleep(2)
    yield [{"type": "text", "text": f"Inquiry email about recent purchase sent to: {args.get('to')}"}]
```

As you can see, the `python_code` and `parameters` YAML properties are passed into the class constructor to make sure the provided code in the YAML
can be used by the function's implementation.

Check out the [example app](https://github.com/definitive-io/openassistants/blob/main/examples/fast-api-server/fast_api_server/main.py) to see how you can add custom functions to the assistant library.
