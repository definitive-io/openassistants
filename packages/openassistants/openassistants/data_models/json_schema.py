from typing import Annotated, Any, Dict

import jsonschema
from pydantic import AfterValidator, TypeAdapter


def _json_schema_meta_validator(value: Any):
    try:
        jsonschema.validate(value, jsonschema.Draft202012Validator.META_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise ValueError(f"Invalid JSONSchema:\n{str(e)}\n") from e
    if value.get("type") != "object":
        raise ValueError(
            f"JSONSchema must have type='object'. Got '{value.get('type')}'"
        )
    return value


JSONSchema = Annotated[Dict[str, Any], AfterValidator(_json_schema_meta_validator)]
"""
A JSONSchema is a dict that conforms to the JSONSchema specification.

In order to validate an arbitrary dict

```
from pydantic import TypeAdapter
json_schema = TypeAdapter(JSONSchema).validate_python(some_dict)
```

When used in a pydantic model as a field, the JSONSchema will be validated automatically.
"""  # noqa: E501


EMPTY_JSON_SCHEMA = TypeAdapter(JSONSchema).validate_python(
    {
        "type": "object",
        "properties": {},
        "required": [],
    }
)
