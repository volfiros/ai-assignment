from collections import deque
from dataclasses import dataclass
import heapq
import time
from typing import Callable, Dict, List, Optional, Set, Tuple

from .core import PuzzleState, get_neighbors, is_goal, is_solvable
from .heuristics import linear_conflict, manhattan_distance


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
HeuristicFn = Callable[[PuzzleState], int]
IdaSearchResult = Tuple[bool, Optional[int], List[PuzzleState], List[str], int, int, int]
HEURISTICS: Dict[str, HeuristicFn] = {
    "manhattan": manhattan_distance,
    "linear_conflict": linear_conflict,
}


def solve_bfs(initial_state: PuzzleState) -> SearchResult:
    started_at = time.perf_counter()
    if not is_solvable(initial_state):
        return _unsolved_result("bfs", started_at)
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
    if not is_solvable(initial_state):
        return _unsolved_result("iddfs", started_at)
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


def solve_astar(initial_state: PuzzleState, heuristic_name: str) -> SearchResult:
    started_at = time.perf_counter()
    if not is_solvable(initial_state):
        return _unsolved_result("astar", started_at, heuristic_name)
    heuristic: HeuristicFn = HEURISTICS[heuristic_name]
    frontier = []
    parents: ParentMap = {initial_state: (None, None)}
    g_scores: Dict[PuzzleState, int] = {initial_state: 0}
    best_expanded = set()
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1
    sequence = 0

    heapq.heappush(frontier, (heuristic(initial_state), sequence, initial_state))

    while frontier:
        _, _, state = heapq.heappop(frontier)
        if state in best_expanded:
            continue

        best_expanded.add(state)
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
                algorithm="astar",
                heuristic=heuristic_name,
            )

        current_cost = g_scores[state]

        for move, neighbor in get_neighbors(state):
            tentative_cost = current_cost + 1
            known_cost = g_scores.get(neighbor)
            if known_cost is not None and tentative_cost >= known_cost:
                continue
            parents[neighbor] = (state, move)
            g_scores[neighbor] = tentative_cost
            sequence += 1
            priority = tentative_cost + heuristic(neighbor)
            heapq.heappush(frontier, (priority, sequence, neighbor))
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
        algorithm="astar",
        heuristic=heuristic_name,
    )


def solve_idastar(initial_state: PuzzleState, heuristic_name: str) -> SearchResult:
    started_at = time.perf_counter()
    if not is_solvable(initial_state):
        return _unsolved_result("idastar", started_at, heuristic_name)

    heuristic: HeuristicFn = HEURISTICS[heuristic_name]
    threshold: int = heuristic(initial_state)
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1

    while True:
        search_result: IdaSearchResult = _ida_search(
            initial_state,
            0,
            threshold,
            heuristic,
            {initial_state},
        )
        found, next_threshold, path, moves, expanded, generated, frontier = search_result
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
                algorithm="idastar",
                heuristic=heuristic_name,
            )

        if next_threshold is None:
            return _unsolved_result(
                "idastar",
                started_at,
                heuristic_name,
                nodes_expanded,
                nodes_generated,
                max_frontier,
            )

        next_limit: int = next_threshold
        threshold = next_limit


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


def _ida_search(
    state: PuzzleState,
    cost: int,
    threshold: int,
    heuristic: HeuristicFn,
    path_states: Set[PuzzleState],
) -> IdaSearchResult:
    estimate = cost + heuristic(state)
    nodes_expanded = 1
    nodes_generated = 0
    max_frontier = len(path_states)

    if estimate > threshold:
        return False, estimate, [], [], nodes_expanded, nodes_generated, max_frontier

    if is_goal(state):
        return True, threshold, [state], [], nodes_expanded, nodes_generated, max_frontier

    minimum: Optional[int] = None

    for move, neighbor in get_neighbors(state):
        if neighbor in path_states:
            continue
        next_path_states = set(path_states)
        next_path_states.add(neighbor)
        nodes_generated += 1
        found, candidate, path, moves, expanded, generated, frontier = _ida_search(
            neighbor,
            cost + 1,
            threshold,
            heuristic,
            next_path_states,
        )
        nodes_expanded += expanded
        nodes_generated += generated
        max_frontier = max(max_frontier, frontier)

        if found:
            return (
                True,
                candidate,
                [state] + path,
                [move] + moves,
                nodes_expanded,
                nodes_generated,
                max_frontier,
            )

        if candidate is not None and (minimum is None or candidate < minimum):
            minimum = candidate

    return False, minimum, [], [], nodes_expanded, nodes_generated, max_frontier


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


def _unsolved_result(
    algorithm: str,
    started_at: float,
    heuristic: Optional[str] = None,
    nodes_expanded: int = 0,
    nodes_generated: int = 0,
    max_frontier: int = 0,
) -> SearchResult:
    return SearchResult(
        solved=False,
        path=[],
        moves=[],
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier=max_frontier,
        elapsed_ms=_elapsed_ms(started_at),
        algorithm=algorithm,
        heuristic=heuristic,
    )
