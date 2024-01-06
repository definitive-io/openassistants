from typing import Annotated, Any, List, Literal, Sequence, Optional,Callable,Dict
import os
import json
import inspect
import pandas as pd

from openassistants.data_models.function_output import FunctionOutput,TextOutput,DataFrameOutput
from openassistants.functions.base import BaseFunction, FunctionExecutionDependency
from openassistants.functions.utils import AsyncStreamVersion
from openassistants.data_models.serialized_dataframe import SerializedDataFrame

from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
import base64


class DogClassificationFunction(BaseFunction):
    type: Literal["DogClassificationFunction"] = "DogClassificationFunction"
    base_path: str
    json_schema: str

    async def execute(
        self, deps: FunctionExecutionDependency
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        
        cwd = os.getcwd()
        os.chdir(self.base_path)
        img_files = [f for f in os.listdir('images/')]
        #with open('/Users/daniel/workspace/openassistants/examples/fast-api-server/dog_classification/schema/dog_classification.json', 'r') as file:
        with open('schema/' + self.json_schema, 'r') as file:
            json_schema = json.load(file)
        for img_file in img_files:
            with open('images/' + img_file, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            output_format = '''
            {{
                "image_id": {img_file_name}
                "num_dogs": value,
                "dog_color": "value",
                "dog_position": "value",
                "background_color": "value"
            }}
            '''.format(img_file_name = img_file[:-4])

            prompt_msg = '''
                Based on the provided SQL data schema and the analysis of the image, please generate a JSON object where each key corresponds to a field in the schema, and each value reflects the characteristics of the image. The output should be in JSON format, suitable for direct use in a dataframe or for other data processing purposes. Here's the schema for reference:

                {json_schema}

                The expected JSON output should be in this format:

                {output_format}

                Please replace value with the actual data extracted from the image.
            '''.format(json_schema = json_schema, output_format = output_format)

            chat = ChatOpenAI(model="gpt-4-vision-preview",
                            max_tokens=1024)
        
            msg = chat.invoke(
                [
                    HumanMessage(
                        content=[
                            {"type": "text", "text":prompt_msg},
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
    
