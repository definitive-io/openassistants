import copy
from io import StringIO
from pathlib import Path
from typing import Iterator, TextIO

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import walk_tree


def _convert_literal_scalarstrings(data: dict | list[dict]):
    data_copy = copy.deepcopy(data)
    walk_tree(data_copy)
    return data_copy


def dump_all(data: list[dict], f: Path | TextIO) -> None:
    data_copy = _convert_literal_scalarstrings(data)
    YAML().dump_all(data_copy, f)


def dumps_all(data: list[dict]) -> str:
    sio = StringIO()
    dump_all(data, sio)
    return sio.getvalue()


def dump(data: dict, f: Path | TextIO) -> None:
    dump_all([data], f)


def dumps(data: dict) -> str:
    return dumps_all([data])


def load(data_raw: str | TextIO | Path) -> dict:
    return YAML().load(data_raw)


def load_all(data_raw: str | TextIO | Path) -> Iterator[dict]:
    return YAML().load_all(data_raw)
