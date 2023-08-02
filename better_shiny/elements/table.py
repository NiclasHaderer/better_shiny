from typing import List

from better_shiny.elements import pandas_element

try:
    import pandas as pd
except ImportError:
    pd = None


def table_element(
    headers: List[str],
    rows: List[List[str]],
):
    if pd is None:
        raise ImportError("Pandas is not installed")

    df = pd.DataFrame(rows, columns=headers)
    return pandas_element(df)
