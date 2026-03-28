import argparse
import sys

from .core import format_state, get_neighbors, is_goal, is_solvable, parse_state
from .presets import PRESET_CASES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="npuzzle")
    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser("solve")
    solve_parser.add_argument("--state")
    solve_parser.add_argument("--case", choices=sorted(PRESET_CASES))

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

    print(render_report(state, source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
