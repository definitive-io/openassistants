import abc
from typing import Dict, Optional, Tuple

from pydantic import BaseModel


class Node(BaseModel):
    @staticmethod
    def build(json_schema: dict):
        if json_schema["type"] == "object":
            return ObjectNode(
                children={
                    k: (k in json_schema.get("required", []), Node.build(v))
                    for k, v in json_schema["properties"].items()
                }
            )
        elif json_schema["type"] == "array":
            return ArrayNode(child=Node.build(json_schema["items"]))
        else:
            return ScalarNode(
                scalar_type=json_schema["type"],
                scalar_format=json_schema.get("format"),
            )


class ScalarNode(Node):
    scalar_type: str
    scalar_format: Optional[str]


class ArrayNode(Node):
    child: Node


class ObjectNode(Node):
    children: Dict[str, Tuple[bool, Node]]


class NodeRepr(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def repr_scalar(cls, scalar_node: ScalarNode) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def repr_array(cls, array_node: ArrayNode) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def repr_object(cls, object_node: ObjectNode) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def repr_optional(cls, node: Node) -> str:
        pass

    @classmethod
    def repr(cls, node: Node):
        if isinstance(node, ScalarNode):
            return cls.repr_scalar(node)
        elif isinstance(node, ArrayNode):
            return cls.repr_array(node)
        elif isinstance(node, ObjectNode):
            return cls.repr_object(node)

    @classmethod
    def repr_json_schema(cls, json_schema: dict):
        return cls.repr(Node.build(json_schema))


class PyRepr(NodeRepr):
    @classmethod
    def repr_object(cls, object_node: ObjectNode) -> str:
        d = []

        for name, (required, child) in object_node.children.items():
            child_repr = cls.repr(child) if required else cls.repr_optional(child)
            d.append(f"{name}: {child_repr}")

        return ", ".join(d)

    @classmethod
    def repr_array(cls, array_node: ArrayNode) -> str:
        return f"List[{cls.repr(array_node.child)}]"

    @classmethod
    def repr_scalar(cls, scalar_node: ScalarNode) -> str:
        mapping: Dict[str, Dict[Optional[str], str]] = {
            "string": {None: "str", "date-time": "datetime", "date": "date"},
            "integer": {None: "int"},
            "number": {None: "float"},
            "boolean": {None: "bool"},
        }
        type_mapping = mapping[scalar_node.scalar_type]
        return type_mapping.get(
            scalar_node.scalar_format, type_mapping[None]
        )  # type: ignore

    @classmethod
    def repr_optional(cls, node: Node) -> str:
        return f"Optional[{cls.repr(node)}]"


if __name__ == "__main__":
    test_json_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "birthdate": {"type": "string", "format": "date"},
            "is_employed": {"type": "boolean"},
            "salary": {"type": "number"},
            "hobbies": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name"],
            },
        },
        "required": ["name", "is_employed"],
    }

    print(PyRepr.repr_json_schema(test_json_schema))
