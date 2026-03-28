import argparse
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from .core import format_state, parse_state
from .presets import PRESET_CASES
from .search import SearchResult, solve_astar, solve_bfs, solve_idastar, solve_iddfs

SOLVERS = {
    "astar": solve_astar,
    "bfs": solve_bfs,
    "idastar": solve_idastar,
    "iddfs": solve_iddfs,
}


class PuzzleController:
    def __init__(self):
        self.selected_case = "medium"
        self.algorithm = "astar"
        self.heuristic = "linear_conflict"
        self.initial_state = PRESET_CASES[self.selected_case]
        self.current_state = self.initial_state
        self.path = [self.current_state]
        self.path_index = 0
        self.result = None

    def set_case(self, case_name: str):
        self.selected_case = case_name
        self.initial_state = PRESET_CASES[case_name]
        self.reset()

    def set_algorithm(self, algorithm: str):
        self.algorithm = algorithm

    def set_heuristic(self, heuristic: str):
        self.heuristic = heuristic

    def set_custom_state(self, text: str):
        self.selected_case = "custom"
        self.initial_state = parse_state(text)
        self.reset()

    def solve(self) -> SearchResult:
        if self.algorithm in {"astar", "idastar"}:
            result = SOLVERS[self.algorithm](self.initial_state, self.heuristic)
        else:
            result = SOLVERS[self.algorithm](self.initial_state)

        self.result = result
        self.path = result.path or [self.initial_state]
        self.path_index = 0
        self.current_state = self.path[self.path_index]
        return result

    def reset(self):
        self.current_state = self.initial_state
        self.path = [self.initial_state]
        self.path_index = 0
        self.result = None

    def next_step(self):
        if self.path_index + 1 < len(self.path):
            self.path_index += 1
            self.current_state = self.path[self.path_index]

    def previous_step(self):
        if self.path_index > 0:
            self.path_index -= 1
            self.current_state = self.path[self.path_index]

    def board_rows(self):
        values = format_state(self.current_state).splitlines()
        return [row.split() for row in values]

    def step_label(self) -> str:
        return f"Step {self.path_index + 1}/{len(self.path)}"

    def metrics(self):
        if self.result is None:
            return [
                ("Solved", "not run"),
                ("Moves", "0"),
                ("Nodes expanded", "0"),
                ("Nodes generated", "0"),
                ("Max frontier", "0"),
                ("Elapsed ms", "0"),
            ]

        return [
            ("Solved", "yes" if self.result.solved else "no"),
            ("Moves", str(len(self.result.moves))),
            ("Nodes expanded", str(self.result.nodes_expanded)),
            ("Nodes generated", str(self.result.nodes_generated)),
            ("Max frontier", str(self.result.max_frontier)),
            ("Elapsed ms", str(self.result.elapsed_ms)),
        ]


class PuzzleApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.controller = PuzzleController()
        self.play_job = None

        self.root.title("N-Puzzle Visualizer")
        self.root.minsize(720, 520)

        self.case_var = tk.StringVar(value=self.controller.selected_case)
        self.algorithm_var = tk.StringVar(value=self.controller.algorithm)
        self.heuristic_var = tk.StringVar(value=self.controller.heuristic)
        self.custom_state_var = tk.StringVar(value="")
        self.speed_var = tk.IntVar(value=350)
        self.step_var = tk.StringVar(value=self.controller.step_label())

        self.tile_labels = []
        self.metric_values = {}

        self._build_layout()
        self.refresh_view()

    def _build_layout(self):
        shell = ttk.Frame(self.root, padding=16)
        shell.pack(fill="both", expand=True)

        shell.columnconfigure(0, weight=1)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(0, weight=1)

        left = ttk.Frame(shell)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        right = ttk.Frame(shell)
        right.grid(row=0, column=1, sticky="nsew")

        controls = ttk.LabelFrame(left, text="Controls", padding=12)
        controls.pack(fill="x")

        ttk.Label(controls, text="Preset case").grid(row=0, column=0, sticky="w")
        case_box = ttk.Combobox(
            controls,
            textvariable=self.case_var,
            values=sorted(PRESET_CASES),
            state="readonly",
        )
        case_box.grid(row=1, column=0, sticky="ew", pady=(4, 10))
        case_box.bind("<<ComboboxSelected>>", self.on_case_changed)

        ttk.Label(controls, text="Algorithm").grid(row=2, column=0, sticky="w")
        algorithm_box = ttk.Combobox(
            controls,
            textvariable=self.algorithm_var,
            values=["astar", "idastar", "bfs", "iddfs"],
            state="readonly",
        )
        algorithm_box.grid(row=3, column=0, sticky="ew", pady=(4, 10))
        algorithm_box.bind("<<ComboboxSelected>>", self.on_algorithm_changed)

        ttk.Label(controls, text="Heuristic").grid(row=4, column=0, sticky="w")
        heuristic_box = ttk.Combobox(
            controls,
            textvariable=self.heuristic_var,
            values=["linear_conflict", "manhattan"],
            state="readonly",
        )
        heuristic_box.grid(row=5, column=0, sticky="ew", pady=(4, 10))
        heuristic_box.bind("<<ComboboxSelected>>", self.on_heuristic_changed)

        ttk.Label(controls, text="Custom state").grid(row=6, column=0, sticky="w")
        custom_entry = ttk.Entry(controls, textvariable=self.custom_state_var)
        custom_entry.grid(row=7, column=0, sticky="ew", pady=(4, 6))

        ttk.Button(controls, text="Load custom", command=self.on_custom_state).grid(
            row=8,
            column=0,
            sticky="ew",
            pady=(0, 10),
        )

        ttk.Label(controls, text="Playback speed (ms)").grid(row=9, column=0, sticky="w")
        speed = ttk.Scale(
            controls,
            from_=100,
            to=1200,
            orient="horizontal",
            variable=self.speed_var,
        )
        speed.grid(row=10, column=0, sticky="ew", pady=(4, 10))

        actions = ttk.Frame(controls)
        actions.grid(row=11, column=0, sticky="ew")
        actions.columnconfigure((0, 1), weight=1)

        ttk.Button(actions, text="Solve", command=self.on_solve).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(actions, text="Reset", command=self.on_reset).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        playback = ttk.Frame(controls)
        playback.grid(row=12, column=0, sticky="ew", pady=(10, 0))
        playback.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(playback, text="Prev", command=self.on_prev).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(playback, text="Play", command=self.on_play).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(playback, text="Next", command=self.on_next).grid(row=0, column=2, sticky="ew", padx=(4, 0))

        controls.columnconfigure(0, weight=1)

        board_frame = ttk.LabelFrame(right, text="Board", padding=12)
        board_frame.pack(fill="both", expand=False)

        grid = ttk.Frame(board_frame)
        grid.pack()

        for row in range(3):
            grid.rowconfigure(row, weight=1)
            grid.columnconfigure(row, weight=1)

        for row in range(3):
            label_row = []
            for col in range(3):
                tile = tk.Label(
                    grid,
                    width=4,
                    height=2,
                    font=("Helvetica", 28, "bold"),
                    relief="ridge",
                    borderwidth=2,
                    bg="#f3f4f6",
                )
                tile.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
                label_row.append(tile)
            self.tile_labels.append(label_row)

        ttk.Label(right, textvariable=self.step_var, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(12, 6))

        metrics = ttk.LabelFrame(right, text="Metrics", padding=12)
        metrics.pack(fill="x", expand=False)

        for index, (name, value) in enumerate(self.controller.metrics()):
            ttk.Label(metrics, text=name).grid(row=index, column=0, sticky="w")
            value_label = ttk.Label(metrics, text=value)
            value_label.grid(row=index, column=1, sticky="e", padx=(16, 0))
            self.metric_values[name] = value_label

        self.move_list = tk.Text(right, height=6, width=32, wrap="word")
        self.move_list.pack(fill="both", expand=True, pady=(12, 0))
        self.move_list.configure(state="disabled")

    def on_case_changed(self, _event=None):
        self.controller.set_case(self.case_var.get())
        self.custom_state_var.set("")
        self.stop_playback()
        self.refresh_view()

    def on_algorithm_changed(self, _event=None):
        self.controller.set_algorithm(self.algorithm_var.get())
        self.refresh_view()

    def on_heuristic_changed(self, _event=None):
        self.controller.set_heuristic(self.heuristic_var.get())
        self.refresh_view()

    def on_custom_state(self):
        try:
            self.controller.set_custom_state(self.custom_state_var.get())
        except ValueError as exc:
            messagebox.showerror("Invalid state", str(exc))
            return
        self.stop_playback()
        self.refresh_view()

    def on_solve(self):
        self.controller.set_algorithm(self.algorithm_var.get())
        self.controller.set_heuristic(self.heuristic_var.get())
        result = self.controller.solve()
        self.stop_playback()
        self.refresh_view()
        if not result.solved:
            messagebox.showinfo("No solution", "This board is unsolvable.")

    def on_reset(self):
        self.stop_playback()
        self.controller.reset()
        self.refresh_view()

    def on_next(self):
        self.stop_playback()
        self.controller.next_step()
        self.refresh_view()

    def on_prev(self):
        self.stop_playback()
        self.controller.previous_step()
        self.refresh_view()

    def on_play(self):
        self.stop_playback()
        self._play_step()

    def _play_step(self):
        self.controller.next_step()
        self.refresh_view()
        if self.controller.path_index + 1 < len(self.controller.path):
            self.play_job = self.root.after(int(self.speed_var.get()), self._play_step)
        else:
            self.play_job = None

    def stop_playback(self):
        if self.play_job is not None:
            self.root.after_cancel(self.play_job)
            self.play_job = None

    def refresh_view(self):
        rows = self.controller.board_rows()
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                tile = self.tile_labels[row_index][col_index]
                if value == "0":
                    tile.configure(text="", bg="#d1d5db")
                else:
                    tile.configure(text=value, bg="#f3f4f6")

        self.step_var.set(self.controller.step_label())

        for name, value in self.controller.metrics():
            self.metric_values[name].configure(text=value)

        moves = "(none)"
        if self.controller.result and self.controller.result.moves:
            moves = " ".join(self.controller.result.moves)
        self.move_list.configure(state="normal")
        self.move_list.delete("1.0", "end")
        self.move_list.insert("1.0", f"Moves: {moves}")
        self.move_list.configure(state="disabled")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="npuzzle.app")
    parser.add_argument("--smoke-test", action="store_true")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.smoke_test:
        PuzzleController()
        print("N-Puzzle visualizer ready")
        return 0
    try:
        root = tk.Tk()
    except Exception as exc:
        print(f"Unable to launch Tkinter app: {exc}", file=sys.stderr)
        return 1
    app = PuzzleApp(root)
    print("N-Puzzle visualizer ready")
    try:
        root.mainloop()
    finally:
        app.stop_playback()
        if root.winfo_exists():
            root.destroy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
