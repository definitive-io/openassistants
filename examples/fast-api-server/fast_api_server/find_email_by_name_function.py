from typing import Sequence

import pandas as pd

from openassistants.contrib.python_callable import PythonCallableFunction
from openassistants.data_models.function_input import BaseJSONSchema
from openassistants.data_models.function_output import FunctionOutput, TextOutput
from openassistants.functions.base import BaseFunctionEntityConfig, FunctionExecutionDependency
from openassistants.functions.utils import AsyncStreamVersion


async def _execute(deps: FunctionExecutionDependency) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
    name = deps.arguments["name"]

    # load csv
    df = pd.read_csv("dummy-data/employees.csv")

    # find email where csv.name == name
    email = df[df["name"] == name]["email"].iloc[0]

    yield [TextOutput(text=f"Found Email For: {name} ({email})")]


async def _get_entity_configs() -> dict[str, BaseFunctionEntityConfig]:
    df = pd.read_csv("dummy-data/employees.csv")
    records = df[["name"]].to_json(index=False, orient="records")
    return {
        "name": BaseFunctionEntityConfig(
            entities=records,
        )
    }


find_email_by_name_function = PythonCallableFunction(
    id="find_email",
    type="FindEmailFunction",
    display_name="Find Email",
    description="Find an email address",
    sample_questions=["Find the email address for {employee}"],
    parameters=BaseJSONSchema(
        json_schema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the person to find the email address for",
                }
            },
            "required": ["name"],
        }
    ),
    execute_callable=_execute,
    get_entity_configs_callable=_get_entity_configs,
)

