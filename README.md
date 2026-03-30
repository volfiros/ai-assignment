# N-Puzzle Solver

This is our Group 28 N-Puzzle Solver project for CS F407 Artificial Intelligence.

It solves the 8-puzzle using four search algorithms:

- `BFS`
- `IDDFS`
- `A*`
- `IDA*`

It also includes two heuristics:

- `Manhattan Distance`
- `Linear Conflict`

Along with the solver, the project has:

- a command-line interface
- a benchmark mode
- a Tkinter visualizer to step through solutions

## Group 28

- `SAI RITHVIK PADMA` (`2021A7PS1632P`)
- `PRATEEK TYAGI` (`2023AAPS0733P`)
- `LAKSHAY YADAV` (`2022A7PS0044P`)

## How the puzzle works

The 8-puzzle is a `3x3` board with tiles `1` to `8` and one blank space, represented by `0`.

The goal state is:

```text
1 2 3
4 5 6
7 8 0
```

At each step, the blank tile can move up, down, left, or right if that move is valid.

## Project structure

```text
npuzzle/
  core.py         puzzle representation and helper functions
  heuristics.py   Manhattan Distance and Linear Conflict
  search.py       BFS, IDDFS, A*, and IDA*
  presets.py      easy, medium, and hard test boards
  cli.py          command-line interface
  app.py          Tkinter visualizer
tests/
  test_core.py
  test_heuristics.py
  test_search.py
  test_cli.py
  test_app.py
```

## Requirements

- Python `3.9`
- Tkinter support in Python

No external packages are needed.

## Setup

```bash
git clone <your-repo-url>
cd ai-assignment
```

## Running the CLI

Show help:

```bash
python3 -m npuzzle.cli --help
```

Check a board without solving it:

```bash
python3 -m npuzzle.cli solve --state "1 2 3 4 5 6 7 8 0"
```

Solve the easy preset with BFS:

```bash
python3 -m npuzzle.cli solve --algorithm bfs --case easy
```

Solve the medium preset with A* and Manhattan Distance:

```bash
python3 -m npuzzle.cli solve --algorithm astar --heuristic manhattan --case medium
```

Solve a custom board with A* and Linear Conflict:

```bash
python3 -m npuzzle.cli solve --algorithm astar --heuristic linear_conflict --state "1 2 3 4 5 6 7 0 8"
```

Run the benchmark:

```bash
python3 -m npuzzle.cli benchmark
```

### Note about heuristics

Heuristics are only used by:

- `A*`
- `IDA*`

They are not used by:

- `BFS`
- `IDDFS`

## Running the visualizer

Start the app:

```bash
python3 -m npuzzle.app
```

Run the smoke test:

```bash
python3 -m npuzzle.app --smoke-test
```

### GUI note

The heuristic dropdown is always visible in the GUI, but it only affects `A*` and `IDA*`. For `BFS` and `IDDFS`, it is ignored.

## Testing

Run all tests:

```bash
python3 -m unittest discover -s tests
```

## Example demo commands

```bash
python3 -m npuzzle.cli solve --algorithm bfs --case easy
python3 -m npuzzle.cli solve --algorithm astar --heuristic linear_conflict --case medium
python3 -m npuzzle.cli benchmark
python3 -m npuzzle.app
```
