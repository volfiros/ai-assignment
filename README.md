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
- a solvability check before search starts

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

Before running any search, the program checks whether the given board is solvable. This avoids wasting time on impossible cases.

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

Solve the hard preset with IDA*:

```bash
python3 -m npuzzle.cli solve --algorithm idastar --heuristic linear_conflict --case hard
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

## Empirical validation

To check whether the implementation behaves the way we discussed in D2, we ran:

```bash
python3 -m npuzzle.cli benchmark
```

These are the current results:

```text
Case    Algorithm  Heuristic        Moves  Expanded  Generated  Frontier
easy    bfs        -                1      4         8          5
easy    iddfs      -                1      5         4          2
easy    astar      linear_conflict  1      2         4          3
easy    idastar    linear_conflict  1      4         4          2
medium  bfs        -                4      33        60         28
medium  iddfs      -                4      68        64         5
medium  astar      linear_conflict  4      5         10         6
medium  idastar    linear_conflict  4      9         9          5
hard    bfs        -                20     55409     74203      18858
hard    iddfs      -                20     506664    506644     21
hard    astar      linear_conflict  20     166       271        106
hard    idastar    linear_conflict  20     314       311        21
```

What this shows:

- all four algorithms solve the easy, medium, and hard preset boards
- `BFS` and `IDDFS` find optimal solutions, but they explore many more states on harder inputs
- `A*` gives the best performance here
- `IDA*` uses much less memory than `BFS`, while still using heuristics

This is our empirical validation of D2: the actual benchmark results follow the same tradeoffs we expected from the analysis.

We also compared the two heuristics on the hard board:

```bash
python3 -m npuzzle.cli solve --algorithm astar --heuristic manhattan --case hard
python3 -m npuzzle.cli solve --algorithm astar --heuristic linear_conflict --case hard
```

Current result:

- `A* + manhattan`: `283` nodes expanded
- `A* + linear_conflict`: `166` nodes expanded

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
