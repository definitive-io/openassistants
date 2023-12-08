import abc
import dataclasses
import textwrap
from typing import List, Optional, Sequence

from langchain.chat_models.base import BaseChatModel
from pydantic import BaseModel

from openassistants.data_models.chat_messages import OpasMessage
from openassistants.data_models.function_output import FunctionOutput
from openassistants.functions.utils import AsyncStreamVersion
from openassistants.utils.json_schema import PyRepr


@dataclasses.dataclass
class FunctionExecutionDependency:
    chat_history: List[OpasMessage]
    arguments: dict
    summarization_chat_model: BaseChatModel


class BaseFunction(BaseModel, abc.ABC):
    id: str
    type: str
    display_name: Optional[str]
    description: str
    sample_questions: List[str]

    @abc.abstractmethod
    async def execute(
        self,
        deps: FunctionExecutionDependency,
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        """
        continually send the up to date outputs
        """
        yield []

    @abc.abstractmethod
    async def get_parameters_json_schema(self) -> dict:
        """
        Get the json schema of the function's parameters
        """
        pass

    async def get_signature(self) -> str:
        json_schema = await self.get_parameters_json_schema()

        # convert JSON Schema types to Python types signature
        params_repr = PyRepr.repr_json_schema(json_schema)

        # Construct the function signature
        signature = f"""\
def {self.id}({params_repr}) -> pd.DataFrame:
    \"\"\"
{textwrap.indent(self.description, "    ")}
    \"\"\"
"""
        return signature

    def get_function_name(self) -> str:
        return f"{self.id}"
