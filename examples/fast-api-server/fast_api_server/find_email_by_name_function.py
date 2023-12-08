from typing import Sequence

import pandas as pd
from openassistants.contrib.python_callable import PythonCallableFunction
from openassistants.data_models.function_input import BaseJSONSchema
from openassistants.data_models.function_output import FunctionOutput, TextOutput
from openassistants.functions.base import FunctionExecutionDependency
from openassistants.functions.utils import AsyncStreamVersion


async def find_email_by_name_callable(
    deps: FunctionExecutionDependency,
) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
    """
    user entities are:
    name | email
    richard | richard@hooli.com
    ...
    """

    name = deps.arguments["name"]

    # load csv
    df = pd.read_csv("dummy-data/employees.csv")

    # find email where csv.name == name
    email = df[df["name"] == name]["email"].iloc[0]

    yield [TextOutput(text=f"Found Email For: {name} ({email})")]


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
    callable=find_email_by_name_callable,
)
