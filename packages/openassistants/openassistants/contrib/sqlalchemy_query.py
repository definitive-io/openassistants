import asyncio
from typing import Annotated, Any, List, Literal, Sequence

import pandas as pd
from langchain.schema import BaseMessage, HumanMessage
from pydantic import Field, PrivateAttr
from sqlalchemy import text
from sqlalchemy.engine import Engine
from starlette.concurrency import run_in_threadpool

from openassistants.data_models.chat_messages import (
    SuggestedPrompt,
    _render_df_for_llm,
    opas_to_lc,
)
from openassistants.data_models.function_input import BaseJSONSchema
from openassistants.data_models.function_output import (
    DataFrameOutput,
    FollowUpsOutput,
    FunctionOutput,
    TextOutput,
    VisualizationOutput,
)
from openassistants.data_models.serialized_dataframe import SerializedDataFrame
from openassistants.functions.base import BaseFunction, FunctionExecutionDependency
from openassistants.functions.visualize import execute_visualization
from openassistants.utils.async_utils import AsyncStreamVersion
from openassistants.utils.strings import resolve_str_template


def run_sql(sqlalchemy_engine: Engine, sql: str, parameters: dict) -> pd.DataFrame:
    with sqlalchemy_engine.connect() as connection:
        # Use SQLAlchemy's text function to create a SQL expression
        # Bind parameters to the SQL expression to prevent SQL injection
        sql = text(sql)
        result = connection.execute(sql, parameters)
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()
    return df


class QueryFunction(BaseFunction):
    type: Literal["QueryFunction"] = "QueryFunction"
    parameters: BaseJSONSchema
    sqls: List[str]
    visualizations: List[str]
    summarization: str
    suggested_follow_ups: Annotated[List[SuggestedPrompt], Field(default_factory=list)]
    _engine: Engine = PrivateAttr()

    async def _execute_sqls(
        self, engine: Engine, deps: FunctionExecutionDependency
    ) -> List[pd.DataFrame]:
        res: List[pd.DataFrame] = await asyncio.gather(  # type: ignore
            *[
                run_in_threadpool(run_sql, engine, sql, deps.arguments)
                for sql in self.sqls
            ]
        )
        return res

    async def _execute_visualizations(
        self, dfs: List[pd.DataFrame], deps: FunctionExecutionDependency
    ) -> List[Any]:
        return await asyncio.gather(  # type: ignore
            *[execute_visualization(viz, dfs) for viz in self.visualizations]
        )

    async def execute_summarization(
        self, dfs: List[pd.DataFrame], deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[str]:
        lc_messages: List[BaseMessage] = opas_to_lc(deps.chat_history, True)

        lc_messages.append(
            HumanMessage(
                content=f"""\
To answer the previous question, I called a function: {self.id}({deps.arguments})
"""
            )
        )
        lc_messages.append(
            HumanMessage(
                content=f"""\
The following table answers the previous question:
{_render_df_for_llm(dfs[0])}

Some details about the table:
{self.description}

Provide a summary based on the data.
"""
            )
        )

        full = ""

        async for response_message in deps.summarization_chat_model.astream(
            lc_messages
        ):
            full += response_message.content
            yield full

    async def execute(
        self,
        deps: FunctionExecutionDependency,
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        self.parameters.validate_args(deps.arguments)

        results: List[FunctionOutput] = []

        dataframes = await self._execute_sqls(self._engine, deps)
        results.extend(
            [
                DataFrameOutput(dataframe=SerializedDataFrame.from_pd(df))
                for df in dataframes
            ]
        )

        yield results

        visualizations = await self._execute_visualizations(dataframes, deps)

        results.extend(
            [VisualizationOutput(visualization=viz) for viz in visualizations]
        )

        yield results

        # Add summarization
        summarization_text = ""

        async for summarization_text in self.execute_summarization(dataframes, deps):
            yield results + [TextOutput(text=summarization_text)]

        results.extend([TextOutput(text=summarization_text)])

        yield results

        # Add follow up questions
        results.extend(
            [
                FollowUpsOutput(
                    follow_ups=[
                        SuggestedPrompt(
                            title=resolve_str_template(template.title, dfs=dataframes),
                            prompt=resolve_str_template(
                                template.prompt, dfs=dataframes
                            ),
                        )
                        for template in self.suggested_follow_ups
                    ]
                )
            ]
        )

        yield results

    async def get_parameters_json_schema(self) -> dict:
        return self.parameters.json_schema
