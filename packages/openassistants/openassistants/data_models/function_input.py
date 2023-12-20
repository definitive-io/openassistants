from typing import Any, Dict

from pydantic import BaseModel

from openassistants.data_models.json_schema import JSONSchema


class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class FunctionInputRequest(FunctionCall):
    json_schema: JSONSchema
