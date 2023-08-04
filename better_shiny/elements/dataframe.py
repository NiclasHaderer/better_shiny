from dataclasses import dataclass

from dominate import tags

from better_shiny import reactive
from better_shiny.reactive import on

try:
    import pandas as pd
except ImportError:
    pd = None


@dataclass
class Sorting:
    column: str | None
    ascending: bool
    reset_on_change: bool


@reactive.dynamic()
def pandas_element(
        df: pd.DataFrame,
) -> tags.table:
    if pd is None:
        raise ImportError("Pandas is not installed")

    sorting = reactive.Value(Sorting(column=None, ascending=True, reset_on_change=False))

    if sorting().column is not None:
        df = df.sort_values(by=sorting().column, ascending=sorting().ascending)

    def adjust_sorting(_, sorting_column: str):
        sorting_value = sorting.value_non_reactive
        if sorting_value.column == sorting_column:
            if sorting_value.reset_on_change:
                sorting.set(Sorting(column=None, ascending=True, reset_on_change=False))
            else:
                sorting.set(Sorting(column=sorting_column, ascending=not sorting_value.ascending, reset_on_change=True))
        else:
            sorting.set(Sorting(column=sorting_column, ascending=True, reset_on_change=False))

    table = tags.table()
    with table:
        with tags.thead():
            with tags.tr():
                for column in df.columns:
                    with tags.th():
                        with tags.div(cls="cursor-pointer flex items-center"):
                            tags.span(column)

                            color = "" if sorting().column == column else "invisible"
                            if sorting().ascending:
                                tags.i("▲", cls=f"select-none ml-1 {color}")
                            else:
                                tags.i("▼", cls=f"select-none ml-1 {color}")
                            on("click", data=column, handler=adjust_sorting)

        with tags.tbody():
            for row in df.itertuples():
                with tags.tr():
                    for value in row[1:]:
                        tags.td(value)
    return table
