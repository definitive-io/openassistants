import os
from typing import List, Literal

import pandas as pd
from sqlalchemy import Engine, create_engine

from openassistants.contrib.sqlalchemy_query import QueryFunction
from openassistants.functions.base import FunctionExecutionDependency


class DuckDBQueryFunction(QueryFunction):
    type: Literal["DuckDBQueryFunction"] = "DuckDBQueryFunction"  # type ignore
    dataset: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._engine = create_engine("duckdb:///:memory:")

    async def _execute_sqls(
        self, engine: Engine, deps: FunctionExecutionDependency
    ) -> List[pd.DataFrame]:
        # Set workdir to the dataset path
        # Capture the current working directory
        cwd = os.getcwd()
        try:
            os.chdir(self.dataset)
            res = await super()._execute_sqls(engine, deps)
        finally:
            # Restore the working directory even if an error occurs
            os.chdir(cwd)

        return res
