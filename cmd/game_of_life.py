from asyncio import Task

from dominate.util import text, container

from better_shiny import reactive
from better_shiny.app import BetterShiny
from dominate.tags import *

from better_shiny.reactive import on, dynamic
from better_shiny.utils import set_interval

app = BetterShiny()

Grid = list[list[int]]


def create_grid(rows: int, cols: int) -> Grid:
    return [[0 for _ in range(cols)] for _ in range(rows)]


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def get_next_generation(grid):
    rows = len(grid)
    cols = len(grid[0])

    # Create a new grid to hold the next generation
    new_grid = [[0] * cols for _ in range(rows)]

    # Define neighbor offsets
    neighbors = [(-1, -1), (-1, 0), (-1, 1),
                 (0, -1), (0, 1),
                 (1, -1), (1, 0), (1, 1)]

    for row in range(rows):
        for col in range(cols):
            live_neighbors = 0

            # Count live neighbors
            for dr, dc in neighbors:
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    live_neighbors += grid[nr][nc]

            # Apply rules of the Game of Life
            if grid[row][col] == 1:
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[row][col] = 0
                else:
                    new_grid[row][col] = 1
            else:
                if live_neighbors == 3:
                    new_grid[row][col] = 1

    return new_grid


@dynamic()
def grid_outlet(grid: reactive.Value[Grid]):
    def toggle_at(_: any, col_row: tuple[int, int]):
        row, col = col_row
        grid_copy = copy_grid(grid())
        grid_copy[row][col] = 1 - grid_copy[row][col]
        grid.set(grid_copy)

    with div() as grid_container:
        attr(cls='grid-container')
        for row_idx in range(len(grid())):
            with div():
                attr(cls='row')
                for col_idx in range(len(grid()[row_idx])):
                    checked = grid()[row_idx][col_idx] == 1
                    with button():
                        attr(cls=f'col {"active" if checked else ""}')
                        on("click", toggle_at, data=(row_idx, col_idx))

    return grid_container


@dynamic()
def start_pause_btn(grid: reactive.Value[Grid]):
    has_started = reactive.Value(False)
    timer = reactive.StableValue[Task | None](None)

    @reactive.on_update(has_started)
    def on_has_started_change(_: reactive.Value[bool]):
        if has_started.value_non_reactive:
            task = set_interval(lambda: grid.set(get_next_generation(grid.value_non_reactive)), 0.01)
            timer.set(task)
        else:
            task = timer()
            if task:
                task.cancel()

    with button():
        on("click", lambda _, __: has_started.set(not has_started.value_non_reactive))
        if has_started():
            text("Pause")
        else:
            text("Start")

    return has_started


@dynamic()
def _index():
    grid = reactive.Value(create_grid(20, 20))
    with container() as c:
        start_pause_btn(grid)
        grid_outlet(grid)
    return c


@app.page('/')
def index():
    with container() as c:
        style("""
        .grid-container {
        }
        .row {
            display: flex;
        }
        .col {
            display: inline-block;
            width: 10px;
            height: 10px;
            border: 1px solid black;
        }
        .active {
            background-color: black;
        }
        """)
        _index()

    return c
