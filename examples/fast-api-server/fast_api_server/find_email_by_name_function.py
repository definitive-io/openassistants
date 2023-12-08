from typing import Sequence

import anyio
import pandas as pd
from openassistants.contrib.python_callable import PythonCallableFunction
from openassistants.data_models.function_input import BaseJSONSchema
from openassistants.data_models.function_output import FunctionOutput, TextOutput
from openassistants.functions.base import (
    Entity,
    EntityConfig,
    FunctionExecutionDependency,
)
from openassistants.functions.utils import AsyncStreamVersion


async def _execute(
    deps: FunctionExecutionDependency,
) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
    name = deps.arguments["name"]

    # load csv
    df = await anyio.to_thread.run_sync(pd.read_csv, "dummy-data/employees.csv")

    # find email where csv.name == name
    filtered = df[df["name"] == name]["email"]

    email = None if len(filtered) == 0 else filtered.iloc[0]

    if email is None:
        yield [
            TextOutput(text=f"Could not find email for: {name}"),
        ]

    else:
        yield [TextOutput(text=f"Found Email For: {name} ({email})")]


async def _get_entity_configs() -> dict[str, EntityConfig]:
    df = await anyio.to_thread.run_sync(pd.read_csv, "dummy-data/employees.csv")

    records = df.to_dict("records")

    return {
        "name": EntityConfig(
            entities=[
                Entity(
                    identity=row["name"],
                    description=row["role"] if isinstance(row["role"], str) else None,
                )
                for row in records
            ],
        )
    }


find_email_by_name_function = PythonCallableFunction(
    id="find_email",
    type="FindEmailFunction",
    display_name="Find Email",
    description="Find an email address",
    sample_questions=[
        "Find the email address for {employee}",
        "What is {employee}'s email address?",
    ],
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
