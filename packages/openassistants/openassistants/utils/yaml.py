import yaml

from pathlib import Path
from typing import Optional, TextIO


def dump(data: dict, f=None) -> Optional[str]:
    return yaml.dump(data, f)
    

def load(data_raw: str | TextIO | Path):
     return yaml.safe_load(data_raw)  # type: ignore
