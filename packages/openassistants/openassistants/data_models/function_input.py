from typing import Any, Dict

import jsonschema
from pydantic import BaseModel


class BaseJSONSchema(BaseModel):
    """
    Validates a json_schema. top level must of the schema must be type object
    """

    json_schema: Dict[str, Any]

    def schema_validator(cls, values):
        jsonschema.validate(
            values["json_schema"], jsonschema.Draft202012Validator.META_SCHEMA
        )
        jsonschema.validate(
            values["json_schema"],
            {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["object"]},
                    "properties": {"type": "object"},
                    "required": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "type",
                ],
            },
        )
        return values

    def validate_args(self, args: dict):
        try:
            jsonschema.validate(args, self.json_schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"invalid function arguments\n{e}")


class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class FunctionInputRequest(FunctionCall, BaseJSONSchema):
    pass
