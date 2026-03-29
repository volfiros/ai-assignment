# N-Puzzle Solver

This repository contains the Deliverable 3 implementation for the N-Puzzle assignment. The project is written in Python 3.9 and includes four search algorithms, two heuristics, a command-line interface, and a Tkinter-based visualizer for stepping through solutions.

## Assignment Scope

The project covers the required Deliverable 3 implementation work:

- BFS
- IDDFS
- A*
- IDA*
- Manhattan Distance
- Linear Conflict
- command-line solving and benchmarking
- Tkinter visualization for board playback

## Requirements

- Python 3.9
- Tkinter support enabled in your Python installation

If your default macOS Python does not launch the GUI correctly, use a Homebrew or python.org Python build with working Tkinter support.

## Setup

Clone the repository and move into the project folder:

```bash
git clone <your-repo-url>
cd ai-assignment
```

No third-party packages are required for this project.

## Running The CLI

Show the available commands:

```bash
python3 -m npuzzle.cli --help
```

Solve a preset board:

```bash
python3 -m npuzzle.cli solve --algorithm bfs --case easy
```

Solve a custom board:

```bash
python3 -m npuzzle.cli solve --algorithm astar --heuristic linear_conflict --state "1 2 3 4 5 6 7 0 8"
```

Run the benchmark mode:

```bash
python3 -m npuzzle.cli benchmark
```

## Running The Visualizer

Launch the Tkinter app:

```bash
python3 -m npuzzle.app
```

Run the smoke test without opening the full window:

```bash
python3 -m npuzzle.app --smoke-test
```

## Supported Algorithms

- `bfs`
- `iddfs`
- `astar`
- `idastar`

## Supported Heuristics

- `manhattan`
- `linear_conflict`
