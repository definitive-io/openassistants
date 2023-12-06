from typing import Any, List

import pandas as pd
from pydantic import BaseModel


class SerializedDataFrame(BaseModel):
    columns: List[str]
    data: List[List[Any]]

    @staticmethod
    def from_pd(df: pd.DataFrame):
        return SerializedDataFrame.model_validate_json(
            df.to_json(orient="split", index=False, date_format="iso")
        )

    def to_pd(self):
        return pd.DataFrame(**self.model_dump())
