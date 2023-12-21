import os
from typing import Literal, Sequence

import pandas as pd
import requests
from openassistants.data_models.function_output import (
    DataFrameOutput,
    FunctionOutput,
    SerializedDataFrame,
    TextOutput,
)
from openassistants.data_models.json_schema import JSONSchema
from openassistants.functions.base import (
    BaseFunction,
    BaseFunctionParameters,
    FunctionExecutionDependency,
)
from openassistants.functions.utils import AsyncStreamVersion
from pydantic import TypeAdapter


async def advisor_query(
    user_query: str,
) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
    outputs = ""

    # Set your Bearer token as an environment variable for security
    BEARER_TOKEN = os.getenv("ADVISOR_BEARER_TOKEN")
    ADVISOR_API_BASE = os.getenv("ADVISOR_API_BASE")

    # Headers for the requests
    HEADERS = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    # Step 1: Find relevant dataset
    recommend_payload = {"prompt": user_query}

    outputs += "Searching for the relevant dataset...  \n"
    yield [TextOutput(text=outputs)]

    response = requests.post(
        ADVISOR_API_BASE + "/v0/datasets/recommend",
        headers=HEADERS,
        json=recommend_payload,
    )
    if response.status_code != 200:
        print("Error in recommend step")
        return

    datasets = response.json().get("datasets")
    if not datasets:
        # Override yield
        yield [TextOutput(text="No relevant datasets found.  \n")]
        return

    outputs += f"Found relevant dataset: `{datasets[0]['id']}`.  \n"
    yield [TextOutput(text=outputs)]

    # Step 2: Generate SQL based on the dataset and user query
    prompt_payload = {"prompt": user_query, "dataset": datasets[0], "timeout": 60}

    outputs += "Generating SQL query...  \n"
    yield [TextOutput(text=outputs)]

    response = requests.post(
        ADVISOR_API_BASE + "/v0/datasets/prompt", headers=HEADERS, json=prompt_payload
    )
    if response.status_code != 200:
        print("Error in prompt step")
        return

    sql_query = response.json().get("response", {}).get("sql")
    if not sql_query:
        print("No SQL query found in prompt response")
        return

    # Step 3: Execute SQL
    execute_payload = {
        "query": {"type": "sql", "sql": sql_query},
        "dataset": datasets[0],
        "timeout": 60,
        "mode": "nonblocking",
    }

    outputs += "Running SQL query...  \n"
    yield [TextOutput(text=outputs)]

    response = requests.post(
        ADVISOR_API_BASE + "/v0/datasets/execute", headers=HEADERS, json=execute_payload
    )
    if response.status_code != 200 or "error" in response.json():
        print("Error in execute step")
        return

    # Parsing the result into a DataFrame
    result = response.json().get("result", {}).get("dataframe", {})
    error = response.json().get("error")

    if error:
        yield [TextOutput(text=f"Failed to execute SQL: {error['message']}")]
    elif result:
        columns = result.get("columns")
        data = result.get("data")

        if not columns or not data:
            print("No data returned in execute step")
            return

        # Override yield
        yield [
            DataFrameOutput(
                dataframe=SerializedDataFrame.from_pd(
                    pd.DataFrame(data, columns=columns)
                )
            ),
            TextOutput(
                text=(
                    f"```sql\n{sql_query}\n```\n\n"
                    "*⚠️ This query was dynamically generated."
                    " Please verify the results.*"
                )
            ),
        ]


class AdvisorFunction(BaseFunction):
    type: Literal["AdvisorFunction"] = "AdvisorFunction"

    description: str = (
        "Take a natural language user query and run it against the Advisor"
        " Text to SQL service. It takes a user question and tries to generate SQL"
        " and return a dataframe containing the requested information. Only use this"
        "function if using advisor is explicitly mentioned by the user."
    )
    display_name: str = "Advisor Text to SQL"

    parameters: BaseFunctionParameters = BaseFunctionParameters(
        json_schema=TypeAdapter(JSONSchema).validate_python(
            {
                "type": "object",
                "properties": {
                    "user_query": {
                        "type": "string",
                        "description": "The query to send to the Advisor",  # noqa: E501
                    }
                },
                "required": ["user_query"],
            }
        )
    )

    async def execute(
        self,
        deps: FunctionExecutionDependency,
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        user_query = deps.arguments["user_query"]
        async for output in advisor_query(user_query):
            yield output
