from .core import GOAL_STATE, PuzzleState

GOAL_POSITIONS = {
    value: divmod(index, 3)
    for index, value in enumerate(GOAL_STATE)
}


def manhattan_distance(state: PuzzleState) -> int:
    total = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        row, col = divmod(index, 3)
        goal_row, goal_col = GOAL_POSITIONS[tile]
        total += abs(row - goal_row) + abs(col - goal_col)
    return total


def linear_conflict(state: PuzzleState) -> int:
    return manhattan_distance(state) + 2 * (
        _count_row_conflicts(state) + _count_column_conflicts(state)
    )


def _count_row_conflicts(state: PuzzleState) -> int:
    conflicts = 0
    for row in range(3):
        row_tiles = []
        for col in range(3):
            tile = state[row * 3 + col]
            if tile == 0:
                continue
            goal_row, goal_col = GOAL_POSITIONS[tile]
            if goal_row == row:
                row_tiles.append(goal_col)
        conflicts += _count_inversions(row_tiles)
    return conflicts


def _count_column_conflicts(state: PuzzleState) -> int:
    conflicts = 0
    for col in range(3):
        column_tiles = []
        for row in range(3):
            tile = state[row * 3 + col]
            if tile == 0:
                continue
            goal_row, goal_col = GOAL_POSITIONS[tile]
            if goal_col == col:
                column_tiles.append(goal_row)
        conflicts += _count_inversions(column_tiles)
    return conflicts


def _count_inversions(values) -> int:
    conflicts = 0
    for index, value in enumerate(values):
        for other in values[index + 1:]:
            if value > other:
                conflicts += 1
    return conflicts
