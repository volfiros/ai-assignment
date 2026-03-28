import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .core import GOAL_STATE, PuzzleState, get_neighbors, is_goal


@dataclass
class SearchResult:
    solved: bool
    path: List[PuzzleState]
    moves: List[str]
    nodes_expanded: int
    nodes_generated: int
    max_frontier: int
    elapsed_ms: int
    algorithm: str
    heuristic: Optional[str]


ParentMap = Dict[PuzzleState, Tuple[Optional[PuzzleState], Optional[str]]]


def solve_bfs(initial_state: PuzzleState) -> SearchResult:
    started_at = time.perf_counter()
    frontier = deque([initial_state])
    parents: ParentMap = {initial_state: (None, None)}
    visited = {initial_state}
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1

    while frontier:
        state = frontier.popleft()
        nodes_expanded += 1

        if is_goal(state):
            path, moves = _build_path(parents, state)
            return SearchResult(
                solved=True,
                path=path,
                moves=moves,
                nodes_expanded=nodes_expanded,
                nodes_generated=nodes_generated,
                max_frontier=max_frontier,
                elapsed_ms=_elapsed_ms(started_at),
                algorithm="bfs",
                heuristic=None,
            )

        for move, neighbor in get_neighbors(state):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parents[neighbor] = (state, move)
            frontier.append(neighbor)
            nodes_generated += 1

        max_frontier = max(max_frontier, len(frontier))

    return SearchResult(
        solved=False,
        path=[],
        moves=[],
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier=max_frontier,
        elapsed_ms=_elapsed_ms(started_at),
        algorithm="bfs",
        heuristic=None,
    )


def solve_iddfs(initial_state: PuzzleState) -> SearchResult:
    started_at = time.perf_counter()
    depth_limit = 0
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1

    while depth_limit <= 31:
        found, path, moves, expanded, generated, frontier = _depth_limited_search(
            initial_state,
            depth_limit,
            {initial_state},
        )
        nodes_expanded += expanded
        nodes_generated += generated
        max_frontier = max(max_frontier, frontier)

        if found:
            return SearchResult(
                solved=True,
                path=path,
                moves=moves,
                nodes_expanded=nodes_expanded,
                nodes_generated=nodes_generated,
                max_frontier=max_frontier,
                elapsed_ms=_elapsed_ms(started_at),
                algorithm="iddfs",
                heuristic=None,
            )

        depth_limit += 1

    return SearchResult(
        solved=False,
        path=[],
        moves=[],
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier=max_frontier,
        elapsed_ms=_elapsed_ms(started_at),
        algorithm="iddfs",
        heuristic=None,
    )


def _depth_limited_search(
    state: PuzzleState,
    depth_limit: int,
    path_states: Set[PuzzleState],
):
    nodes_expanded = 1
    nodes_generated = 0
    max_frontier = len(path_states)

    if is_goal(state):
        return True, [state], [], nodes_expanded, nodes_generated, max_frontier

    if depth_limit == 0:
        return False, [], [], nodes_expanded, nodes_generated, max_frontier

    for move, neighbor in get_neighbors(state):
        if neighbor in path_states:
            continue
        next_path_states = set(path_states)
        next_path_states.add(neighbor)
        nodes_generated += 1
        found, path, moves, expanded, generated, frontier = _depth_limited_search(
            neighbor,
            depth_limit - 1,
            next_path_states,
        )
        nodes_expanded += expanded
        nodes_generated += generated
        max_frontier = max(max_frontier, frontier)
        if found:
            return (
                True,
                [state] + path,
                [move] + moves,
                nodes_expanded,
                nodes_generated,
                max_frontier,
            )

    return False, [], [], nodes_expanded, nodes_generated, max_frontier


def _build_path(parents: ParentMap, goal_state: PuzzleState):
    path = []
    moves = []
    state: Optional[PuzzleState] = goal_state

    while state is not None:
        path.append(state)
        parent, move = parents[state]
        if move is not None:
            moves.append(move)
        state = parent

    path.reverse()
    moves.reverse()
    return path, moves


def _elapsed_ms(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)
