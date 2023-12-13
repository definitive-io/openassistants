from typing import Any, List, Optional

import pandas as pd
from openassistants.data_models.chat_messages import (
    OpasAssistantMessage,
    OpasFunctionMessage,
    OpasMessage,
    OpasUserMessage,
)
from openassistants.data_models.function_output import DataFrameOutput, TextOutput
from pydantic import BaseModel


def _render_df_for_llm(df: pd.DataFrame) -> str:
    if len(df) == 0:
        return "Data Not Available."

    return df.to_csv(index=False, date_format="iso")


class Interaction(BaseModel):
    # start
    user_prompt: str

    # terminate or requesting user args
    assistant_response: Optional[str] = None

    # user provides args
    user_provided_args: Optional[Any] = None

    # function invocation
    function_name: Optional[str] = None
    function_arguments: Optional[Any] = None

    function_output_data: Optional[str] = None
    function_output_summary: Optional[str] = None


def opas_to_interactions(
    chat_history: List[OpasMessage],
) -> List[Interaction]:
    current_interaction = Interaction(user_prompt="PLACEHOLDER")

    interaction_list = []

    for message in chat_history:
        match message:
            case OpasUserMessage(
                role="user", content=content, input_response=input_response
            ):
                if input_response is None:
                    # start of new user "interaction"
                    # append previous user interaction to list
                    interaction_list.append(current_interaction)
                    current_interaction = Interaction(user_prompt=content)
                else:
                    current_interaction.user_provided_args = input_response.arguments
            case OpasAssistantMessage(
                role="assistant",
                content=content,
                input_request=None,
                function_call=function_call,
            ):
                if function_call is None:
                    current_interaction.assistant_response = content
                else:
                    current_interaction.function_name = function_call.name
                    current_interaction.function_arguments = function_call.arguments
            case OpasFunctionMessage(role="function", outputs=outputs):
                for output in outputs:
                    if isinstance(output, DataFrameOutput):
                        current_interaction.function_output_data = (
                            (current_interaction.function_output_data or "")
                            + "\n\n"
                            + _render_df_for_llm(output.dataframe.to_pd())
                        )
                    elif isinstance(output, TextOutput):
                        current_interaction.function_output_summary = output.text
                if current_interaction.function_output_data is not None:
                    current_interaction.function_output_data = (
                        current_interaction.function_output_data.strip()
                    )
                if current_interaction.function_output_summary is not None:
                    current_interaction.function_output_summary = (
                        current_interaction.function_output_summary.strip()
                    )

    # append last interaction
    interaction_list.append(current_interaction)
    # drop placeholder
    interaction_list = interaction_list[1:]

    return interaction_list
