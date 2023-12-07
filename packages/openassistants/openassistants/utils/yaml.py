import copy
from io import StringIO
from pathlib import Path
from typing import Optional, TextIO

from ruamel.yaml import YAML  # type: ignore
from ruamel.yaml.scalarstring import walk_tree  # type: ignore


def dump(data: dict, f=None) -> Optional[str]:
    data_copy = copy.deepcopy(data)
    walk_tree(data_copy)
    # if f is none, use string io
    sio = None

    if f is None:
        sio = StringIO()
        f = sio

    YAML().dump(data_copy, f)

    return sio.getvalue() if sio is not None else None


def load(data_raw: str | TextIO | Path):
    return YAML().load(data_raw)
