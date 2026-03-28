from typing import List, Tuple

PuzzleState = Tuple[int, ...]
Neighbor = Tuple[str, PuzzleState]

GOAL_STATE: PuzzleState = (1, 2, 3, 4, 5, 6, 7, 8, 0)
MOVE_ORDER = (
    ("up", -1, 0),
    ("down", 1, 0),
    ("left", 0, -1),
    ("right", 0, 1),
)


def parse_state(text: str) -> PuzzleState:
    tokens = text.replace(",", " ").split()
    if len(tokens) != 9:
        raise ValueError("state must contain exactly 9 tiles")

    try:
        values = tuple(int(token) for token in tokens)
    except ValueError as exc:
        raise ValueError("state must contain only integers") from exc

    if set(values) != set(range(9)):
        raise ValueError("state must contain each tile from 0 to 8 exactly once")

    return values


def format_state(state: PuzzleState) -> str:
    rows = []
    for index in range(0, len(state), 3):
        rows.append(" ".join(str(value) for value in state[index:index + 3]))
    return "\n".join(rows)


def is_goal(state: PuzzleState) -> bool:
    return state == GOAL_STATE


def get_neighbors(state: PuzzleState) -> List[Neighbor]:
    blank_index = state.index(0)
    row, col = divmod(blank_index, 3)
    neighbors: List[Neighbor] = []

    for move, row_delta, col_delta in MOVE_ORDER:
        next_row = row + row_delta
        next_col = col + col_delta
        if not (0 <= next_row < 3 and 0 <= next_col < 3):
            continue

        swap_index = next_row * 3 + next_col
        tiles = list(state)
        tiles[blank_index], tiles[swap_index] = tiles[swap_index], tiles[blank_index]
        neighbors.append((move, tuple(tiles)))

    return neighbors


def inversion_count(state: PuzzleState) -> int:
    tiles = [value for value in state if value != 0]
    inversions = 0

    for index, value in enumerate(tiles):
        for other in tiles[index + 1:]:
            if value > other:
                inversions += 1

    return inversions


def is_solvable(state: PuzzleState) -> bool:
    return inversion_count(state) % 2 == 0
