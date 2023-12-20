import abc
import asyncio
from typing import Annotated, Any, List, Literal, Sequence

import jsonschema
import pandas as pd
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from openassistants.data_models.chat_messages import (
    OpasAssistantMessage,
    OpasFunctionMessage,
    OpasMessage,
)
from openassistants.data_models.function_input import (
    FunctionCall,
)
from openassistants.data_models.function_output import (
    DataFrameOutput,
    FollowUpsOutput,
    FunctionOutput,
    SuggestedPrompt,
    TextOutput,
    VisualizationOutput,
)
from openassistants.data_models.serialized_dataframe import SerializedDataFrame
from openassistants.functions.base import BaseFunction, FunctionExecutionDependency
from openassistants.functions.visualize import execute_visualization
from openassistants.utils import yaml
from openassistants.utils.async_utils import AsyncStreamVersion
from openassistants.utils.history_representation import opas_to_interactions
from openassistants.utils.langchain_util import string_from_message
from openassistants.utils.strings import resolve_str_template
from pydantic import Field, PrivateAttr
from sqlalchemy import text
from sqlalchemy.engine import Engine
from starlette.concurrency import run_in_threadpool


def run_sql(sqlalchemy_engine: Engine, sql: str, parameters: dict) -> pd.DataFrame:
    with sqlalchemy_engine.connect() as connection:
        # Use SQLAlchemy's text function to create a SQL expression
        # Bind parameters to the SQL expression to prevent SQL injection
        result = connection.execute(text(sql), parameters)
        df = pd.DataFrame(result.fetchall())
        df.columns = pd.Index([str(key) for key in result.keys()])
    return df


def _opas_to_summarization_lc(
    chat_history: List[OpasMessage],
) -> List[BaseMessage]:
    lc_messages: List[BaseMessage] = []

    interaction_list = opas_to_interactions(chat_history)

    for interaction in interaction_list:
        user_serialized_yaml = yaml.dumps(
            interaction.model_dump(
                mode="json",
                exclude={"function_output_summary"},
                exclude_none=True,
            ),
        )
        lc_messages.append(HumanMessage(content=user_serialized_yaml))
        # we are trying to predict summarization, so in the few shots, the summarization is the assistants AIMessage  # noqa: E501
        if interaction.function_output_summary is not None:
            lc_messages.append(AIMessage(content=interaction.function_output_summary))

    return lc_messages


class QueryFunction(BaseFunction, abc.ABC):
    type: Literal["QueryFunction"] = "QueryFunction"
    sqls: List[str]
    visualizations: List[str]
    summarization: str
    suggested_follow_ups: Annotated[List[SuggestedPrompt], Field(default_factory=list)]

    @abc.abstractmethod
    async def _execute_sqls(
        self, deps: FunctionExecutionDependency
    ) -> List[pd.DataFrame]:
        pass

    async def _execute_visualizations(
        self, dfs: List[pd.DataFrame], deps: FunctionExecutionDependency
    ) -> List[Any]:
        return await asyncio.gather(  # type: ignore
            *[execute_visualization(viz, dfs) for viz in self.visualizations]
        )

    async def _execute_summarization(
        self, dfs: List[pd.DataFrame], deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[str]:
        chat_continued = [
            *deps.chat_history,
            OpasAssistantMessage(
                content="",
                function_call=FunctionCall(
                    name=self.id,
                    arguments=deps.arguments,
                ),
            ),
            OpasFunctionMessage(
                name=self.id,
                outputs=[
                    DataFrameOutput(dataframe=SerializedDataFrame.from_pd(df))
                    for df in dfs
                ],
            ),
        ]

        system_prompt = """\
You are a helpful assistant

The user invoked functions that provides data to answer the user's prompts.

You will:
* Summarize the function_output_data to respond to the user_prompt.
* Only include statements derived from function_output_data.
* Do not reveal the function call to the user.
* The dataframe is already shown to the user, do not repeat it.
* The text will be rendered as markdown.
"""

        lc_messages: List[BaseMessage] = [
            SystemMessage(content=system_prompt)
        ] + _opas_to_summarization_lc(chat_continued)

        # append function description
        lc_messages[-1].content += "\n" + yaml.dumps(  # type: ignore
            dict(
                function_description=self.description,
                summarization_instructions=self.summarization,
            ),
        )

        full: str = ""

        async for response_message in deps.summarization_chat_model.astream(
            lc_messages,
            {"tags": ["summarization"]},
        ):
            full += string_from_message(response_message)
            yield full

    async def execute(
        self,
        deps: FunctionExecutionDependency,
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        try:
            jsonschema.validate(deps.arguments, self.get_parameters_json_schema())
        except jsonschema.ValidationError as e:
            raise ValueError(f"Invalid arguments:\n{str(e)}") from e

        results: List[FunctionOutput] = []

        dataframes = await self._execute_sqls(deps)
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

        async for summarization_text in self._execute_summarization(dataframes, deps):
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


class SQLAlchemyFunction(QueryFunction, abc.ABC):
    _engine: Engine = PrivateAttr()

    def __init__(self, engine: Engine, **kwargs):
        super().__init__(**kwargs)
        self._engine = engine

    async def _execute_sqls(
        self, deps: FunctionExecutionDependency
    ) -> List[pd.DataFrame]:
        res: List[pd.DataFrame] = await asyncio.gather(  # type: ignore
            *[
                run_in_threadpool(run_sql, self._engine, sql, deps.arguments)
                for sql in self.sqls
            ]
        )
        return res
