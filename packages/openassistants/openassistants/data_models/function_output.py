from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

from openassistants.data_models.serialized_dataframe import SerializedDataFrame


class SuggestedPrompt(BaseModel):
    title: str
    prompt: str


class DataFrameOutput(BaseModel):
    type: Literal["dataframe"] = "dataframe"
    dataframe: SerializedDataFrame


class VisualizationOutput(BaseModel):
    type: Literal["visualization"] = "visualization"
    visualization: Any


class TextOutput(BaseModel):
    type: Literal["text"] = "text"
    text: str


class FollowUpsOutput(BaseModel):
    type: Literal["follow_ups"] = "follow_ups"
    follow_ups: Annotated[list[SuggestedPrompt], Field(default_factory=list)]


FunctionOutput = Annotated[
    DataFrameOutput | VisualizationOutput | TextOutput | FollowUpsOutput,
    Field(json_schema_extra={"descriminator": "type"}),
]
