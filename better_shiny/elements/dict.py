from typing import List, Any, Dict

from better_shiny.elements import pandas_element

try:
    import pandas as pd
except ImportError:
    pd = None


def dict_element(
    dictionary: Dict[str, List[Any]],
):
    if pd is None:
        raise ImportError("Pandas is not installed")

    df = pd.DataFrame(dictionary)
    return pandas_element(df)
