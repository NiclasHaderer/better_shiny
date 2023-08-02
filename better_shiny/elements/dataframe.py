from dominate import tags

try:
    import pandas as pd
except ImportError:
    pd = None


# TODO: Sorting, limiting, etc.
def pandas_element(
    df: pd.DataFrame,
) -> tags.table:
    if pd is None:
        raise ImportError("Pandas is not installed")

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
