import argparse
import sys

from .core import format_state, get_neighbors, is_goal, is_solvable, parse_state
from .presets import PRESET_CASES
from .search import HEURISTICS, solve_astar, solve_bfs, solve_idastar, solve_iddfs

SOLVERS = {
    "astar": solve_astar,
    "bfs": solve_bfs,
    "idastar": solve_idastar,
    "iddfs": solve_iddfs,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="npuzzle")
    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser("solve")
    solve_parser.add_argument("--state")
    solve_parser.add_argument("--case", choices=sorted(PRESET_CASES))
    solve_parser.add_argument("--algorithm", choices=sorted(SOLVERS))
    solve_parser.add_argument("--heuristic", choices=sorted(HEURISTICS))

    return parser


def resolve_state(args: argparse.Namespace):
    if args.state and args.case:
        raise ValueError("use either --state or --case, not both")
    if args.state:
        return parse_state(args.state), "custom"
    if args.case:
        return PRESET_CASES[args.case], args.case
    return PRESET_CASES["easy"], "easy"


def render_report(state, source: str) -> str:
    moves = ", ".join(move for move, _ in get_neighbors(state))
    return "\n".join(
        [
            f"Source: {source}",
            "Board:",
            format_state(state),
            f"State is solvable: {'yes' if is_solvable(state) else 'no'}",
            f"Goal reached: {'yes' if is_goal(state) else 'no'}",
            f"Legal moves: {moves}",
        ]
    )


def render_search_report(state, source: str, algorithm: str, heuristic: str = None) -> str:
    if algorithm in {"astar", "idastar"}:
        result = SOLVERS[algorithm](state, heuristic)
    else:
        result = SOLVERS[algorithm](state)
    moves = " ".join(result.moves) if result.moves else "(none)"
    lines = [
        f"Source: {source}",
        f"Algorithm: {result.algorithm}",
        "Board:",
        format_state(state),
        f"Solved: {'yes' if result.solved else 'no'}",
        f"Move count: {len(result.moves)}",
        f"Moves: {moves}",
        f"Nodes expanded: {result.nodes_expanded}",
        f"Nodes generated: {result.nodes_generated}",
        f"Max frontier: {result.max_frontier}",
        f"Elapsed ms: {result.elapsed_ms}",
    ]
    if result.heuristic:
        lines.insert(2, f"Heuristic: {result.heuristic}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "solve":
        parser.error("unsupported command")

    try:
        state, source = resolve_state(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.algorithm:
        if args.algorithm in {"astar", "idastar"} and not args.heuristic:
            print(f"Error: --heuristic is required for {args.algorithm}", file=sys.stderr)
            return 2
        print(render_search_report(state, source, args.algorithm, args.heuristic))
        return 0

    print(render_report(state, source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
