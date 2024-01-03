from typing import Annotated, Any, List, Literal, Sequence, Optional,Callable,Dict
import os
import inspect
import pandas as pd

from openassistants.data_models.function_input import BaseJSONSchema
from openassistants.data_models.function_output import FunctionOutput,TextOutput,DataFrameOutput
from openassistants.functions.base import BaseFunction, FunctionExecutionDependency
from openassistants.functions.utils import AsyncStreamVersion
from openassistants.data_models.serialized_dataframe import SerializedDataFrame

from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
import base64


class ImageAnalysisFunction(BaseFunction):
    type: Literal["ImageAnalysisFunction"] = "ImageAnalysisFunction"
    parameters: BaseJSONSchema
    image_path: str
    file_name: str

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        
        cwd = os.getcwd()
        os.chdir(self.image_path)
        with open(self.file_name, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        chat = ChatOpenAI(model="gpt-4-vision-preview",
                        max_tokens=1024)
        
        msg = chat.invoke(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text":'Summarize this image in detail'},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
            ]
                )
            ]
        )
        summarization = msg.content

        os.chdir(cwd)
        yield [{"type": "text", "text": summarization}]
    
    async def get_parameters_json_schema(self) -> dict:
        return self.parameters.json_schema
