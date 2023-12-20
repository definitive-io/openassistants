from typing import Annotated, List, Literal, Sequence
import pandas as pd

from openassistants.data_models.function_output import FunctionOutput,TextOutput,SuggestedPrompt,FollowUpsOutput
from openassistants.functions.base import BaseFunction, FunctionExecutionDependency
from openassistants.functions.utils import AsyncStreamVersion
from openassistants.utils.strings import resolve_str_template
from pydantic import Field


class TextResponseFunction(BaseFunction):
    type: Literal["TextResponseFunction"] = "TextRespnseFunction"
    text_response: str
    suggested_follow_ups: Annotated[List[SuggestedPrompt], Field(default_factory=list)]

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        
        results: List[FunctionOutput] = []
        

        results.extend([TextOutput(text=self.text_response)])
        yield results

        # Add follow up questions
        results.extend(
            [
                FollowUpsOutput(
                    follow_ups=[
                        SuggestedPrompt(
                            title=resolve_str_template(template.title, dfs=pd.DataFrame()),
                            prompt=resolve_str_template(
                                template.prompt, dfs=pd.DataFrame()
                            ),
                        )
                        for template in self.suggested_follow_ups
                    ]
                )
            ]
        )
        yield results