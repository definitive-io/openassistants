import abc
import dataclasses
import textwrap
from typing import List, Mapping, Optional, Sequence

from langchain_core.language_models import BaseChatModel
from openassistants.data_models.chat_messages import OpasMessage
from openassistants.data_models.function_output import FunctionOutput
from openassistants.data_models.json_schema import EMPTY_JSON_SCHEMA, JSONSchema
from openassistants.functions.utils import AsyncStreamVersion
from openassistants.utils.json_schema import PyRepr
from pydantic import BaseModel


@dataclasses.dataclass
class FunctionExecutionDependency:
    chat_history: List[OpasMessage]
    arguments: dict
    summarization_chat_model: BaseChatModel


class IEntity(abc.ABC):
    @abc.abstractmethod
    def get_identity(self) -> str:
        pass

    @abc.abstractmethod
    def get_description(self) -> Optional[str]:
        pass


class IEntityConfig(abc.ABC):
    @abc.abstractmethod
    def get_entities(self) -> Sequence[IEntity]:
        pass


class IBaseFunction(abc.ABC):
    @abc.abstractmethod
    def get_id(self) -> str:
        pass

    @abc.abstractmethod
    def get_type(self) -> str:
        pass

    @abc.abstractmethod
    def get_display_name(self) -> Optional[str]:
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        pass

    @abc.abstractmethod
    def get_sample_questions(self) -> Sequence[str]:
        pass

    @abc.abstractmethod
    def get_parameters_json_schema(self) -> JSONSchema:
        """
        Get the json schema of the function's parameters
        """
        pass

    @abc.abstractmethod
    def get_confirm(self) -> bool:
        pass

    def get_signature(self) -> str:
        # convert JSON Schema types to Python types signature
        params_repr = PyRepr.repr_json_schema(self.get_parameters_json_schema())

        sample_question_text = "\n".join(f"* {q}" for q in self.get_sample_questions())

        documentation = f"""\
{self.get_description()}
Example Questions:
{sample_question_text}
"""

        # Construct the function signature
        signature = f"""\
def {self.get_id()}({params_repr}) -> pd.DataFrame:
    \"\"\"
{textwrap.indent(documentation, "    ")}
    \"\"\"
"""
        return signature

    @abc.abstractmethod
    async def get_entity_configs(self) -> Mapping[str, IEntityConfig]:
        pass

    @abc.abstractmethod
    async def execute(
        self,
        deps: FunctionExecutionDependency,
    ) -> AsyncStreamVersion[Sequence[FunctionOutput]]:
        """
        continually send the up to date outputs
        """
        yield []


class Entity(IEntity, BaseModel):
    identity: str
    description: Optional[str] = None

    def get_identity(self) -> str:
        return self.identity

    def get_description(self) -> Optional[str]:
        return self.description


class EntityConfig(IEntityConfig, BaseModel):
    entities: List[Entity]

    def get_entities(self) -> Sequence[IEntity]:
        return self.entities


class BaseFunctionParameters(BaseModel):
    json_schema: JSONSchema = EMPTY_JSON_SCHEMA


class BaseFunction(IBaseFunction, BaseModel, abc.ABC):
    id: str
    type: str
    display_name: Optional[str] = None
    description: str
    sample_questions: List[str] = []
    confirm: bool = False
    parameters: BaseFunctionParameters = BaseFunctionParameters()

    def get_id(self) -> str:
        return self.id

    def get_type(self) -> str:
        return self.type

    def get_display_name(self) -> Optional[str]:
        return self.display_name

    def get_description(self) -> str:
        return self.description

    def get_sample_questions(self) -> Sequence[str]:
        return self.sample_questions

    def get_confirm(self) -> bool:
        return self.confirm

    def get_parameters_json_schema(self) -> JSONSchema:
        return self.parameters.json_schema

    async def get_entity_configs(self) -> Mapping[str, IEntityConfig]:
        return {}
