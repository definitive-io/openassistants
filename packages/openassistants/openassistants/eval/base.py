import abc
import dataclasses
from typing import Dict, List

from pydantic import create_model
from pydantic.fields import FieldInfo


class Validation(abc.ABC):
    @abc.abstractmethod
    def prop_schema(self):
        pass


@dataclasses.dataclass
class PatternValidation(Validation):
    pattern: str

    def prop_schema(self):
        return {
            "type": "string",
            "pattern": self.pattern,
        }


@dataclasses.dataclass
class PydanticValidation(Validation):
    argument: FieldInfo
    argument_type: type

    def prop_schema(self):
        PydanticModel = create_model(
            "PydanticModel", argument=(self.argument_type, self.argument)
        )

        schema = PydanticModel.schema()

        value_properties = schema.get("properties", {}).get("argument", {})
        return value_properties


def json_schema(schema: Dict[str, Validation], required: List[str]):
    return {
        "type": "object",
        "properties": {
            key: validation.prop_schema() for key, validation in schema.items()
        },
        "required": required,
    }
