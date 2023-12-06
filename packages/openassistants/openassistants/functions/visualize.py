from typing import Any

import pandas as pd


async def execute_visualization(
    code: str,
    data: Any,
) -> Any:
    exec_locals = {"pd": pd}

    exec(code, {}, exec_locals)

    chart_config = exec_locals["create_chart_config"](data)  # type: ignore

    result = {
        "width": 600,
        "height": 400,
        "type": "column2d",
        "dataFormat": "json",
        "dataSource": chart_config,
    }
    return result
