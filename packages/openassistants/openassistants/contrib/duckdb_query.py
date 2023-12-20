import os
from typing import List, Literal

import pandas as pd
from openassistants.contrib.sqlalchemy_query import SQLAlchemyFunction
from openassistants.functions.base import FunctionExecutionDependency
from sqlalchemy import create_engine


class DuckDBQueryFunction(SQLAlchemyFunction):
    type: Literal["DuckDBQueryFunction"] = "DuckDBQueryFunction"  # type: ignore
    dataset: str

    def __init__(self, **kwargs):
        super().__init__(engine=create_engine("duckdb:///:memory:"), **kwargs)

    async def _execute_sqls(
        self, deps: FunctionExecutionDependency
    ) -> List[pd.DataFrame]:
        # Set workdir to the dataset path
        # Capture the current working directory
        cwd = os.getcwd()
        try:
            os.chdir(self.dataset)
            res = await super()._execute_sqls(deps)
        finally:
            # Restore the working directory even if an error occurs
            os.chdir(cwd)

        return res
