import os
from typing import List, Literal, Annotated, Sequence

import pandas as pd
from openassistants.contrib.sqlalchemy_query import QueryFunction
from openassistants.functions.base import FunctionExecutionDependency
from openassistants.data_models.serialized_dataframe import SerializedDataFrame
from openassistants.utils.strings import resolve_str_template
from openassistants.utils.async_utils import AsyncStreamVersion
from openassistants.data_models.function_input import BaseJSONSchema, FunctionCall
from openassistants.data_models.function_output import (
    DataFrameOutput,
    FollowUpsOutput,
    FunctionOutput,
    SuggestedPrompt,
    TextOutput,
    VisualizationOutput,
)
from sqlalchemy import Engine, create_engine
from pydantic import Field


class DuckDBQueryFunction(QueryFunction):
    type: Literal["DuckDBQueryFunction"] = "DuckDBQueryFunction"  # type: ignore
    parameters: BaseJSONSchema
    dataset: str
    visualizations: List[str]
    summarization: str
    suggested_follow_ups: Annotated[List[SuggestedPrompt], Field(default_factory=list)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._engine = create_engine("duckdb:///:memory:")

    async def _execute_sqls(
        self, engine: Engine, deps: FunctionExecutionDependency
    ) -> List[pd.DataFrame]:
        # Set workdir to the dataset path
        # Capture the current working directory
        cwd = os.getcwd()
        try:
            os.chdir(self.dataset)
            res = await super()._execute_sqls(engine, deps)
        finally:
            # Restore the working directory even if an error occurs
            os.chdir(cwd)

        return res
    
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
