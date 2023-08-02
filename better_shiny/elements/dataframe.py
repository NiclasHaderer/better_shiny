import pandas as pd
from dominate import tags


# TODO: Sorting, limiting, etc.
def pandas_element(
        df: pd.DataFrame,
) -> tags.table:
    table = tags.table()
    with table:
        with tags.thead():
            with tags.tr():
                for column in df.columns:
                    tags.th(column)

        with tags.tbody():
            for row in df.itertuples():
                with tags.tr():
                    for value in row[1:]:
                        tags.td(value)

    return table
