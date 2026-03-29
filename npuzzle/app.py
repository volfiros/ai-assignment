import argparse
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from .core import format_state, parse_state
from .presets import PRESET_CASES
from .search import SearchResult, solve_astar, solve_bfs, solve_idastar, solve_iddfs

BUTTON_DARK_BG = "#30271e"
BUTTON_DARK_FG = "#f8f4ed"
BUTTON_DARK_ACTIVE_BG = "#46392c"
PLAYBACK_SPEED_DEFAULT = 600
ALGORITHM_LABELS = {
    "astar": "A*",
    "bfs": "BFS",
    "idastar": "IDA*",
    "iddfs": "IDDFS",
}
HEURISTIC_LABELS = {
    "linear_conflict": "Linear Conflict",
    "manhattan": "Manhattan",
}

SOLVERS = {
    "astar": solve_astar,
    "bfs": solve_bfs,
    "idastar": solve_idastar,
    "iddfs": solve_iddfs,
}


class ActionButton(tk.Label):
    def __init__(
        self,
        master,
        text: str,
        command,
        bg: str = BUTTON_DARK_BG,
        fg: str = BUTTON_DARK_FG,
        active_bg: str = BUTTON_DARK_ACTIVE_BG,
        padx: int = 10,
        pady: int = 8,
        font=("Helvetica", 11, "bold"),
    ):
        super().__init__(
            master,
            text=text,
            bg=bg,
            fg=fg,
            padx=padx,
            pady=pady,
            font=font,
            relief="flat",
            cursor="hand2",
            anchor="center",
            takefocus=1,
        )
        self.command = command
        self.default_bg = bg
        self.active_bg = active_bg

        self.bind("<Button-1>", self._on_click)
        self.bind("<Return>", self._on_click)
        self.bind("<space>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<FocusIn>", self._on_enter)
        self.bind("<FocusOut>", self._on_leave)

    def _on_click(self, _event=None):
        self.command()

    def _on_enter(self, _event=None):
        self.configure(bg=self.active_bg)

    def _on_leave(self, _event=None):
        self.configure(bg=self.default_bg)


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

    def move_text(self) -> str:
        if self.result and self.result.moves:
            return " ".join(self.result.moves)
        return "(none)"

    def source_text(self) -> str:
        if self.selected_case == "custom":
            return "Custom board"
        return f"Preset: {self.selected_case}"

    def run_text(self) -> str:
        if self.algorithm in {"astar", "idastar"}:
            return f"{display_algorithm(self.algorithm)} • {display_heuristic(self.heuristic)}"
        return display_algorithm(self.algorithm)

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
        self.root.geometry("1040x680")
        self.root.minsize(960, 620)
        self.root.configure(bg="#f3efe7")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f3efe7")
        style.configure("Rail.TFrame", background="#ebe4d7")
        style.configure("Rail.TLabel", background="#ebe4d7", foreground="#201b16")
        style.configure("Section.TLabel", background="#ebe4d7", foreground="#201b16", font=("Helvetica", 12, "bold"))
        style.configure("Meta.TLabel", background="#fcfaf6", foreground="#5a5146", font=("Helvetica", 11))
        style.configure("App.TCombobox", padding=6)
        style.configure("App.TEntry", padding=6)

        self.case_var = tk.StringVar(value=self.controller.selected_case)
        self.algorithm_var = tk.StringVar(value=display_algorithm(self.controller.algorithm))
        self.heuristic_var = tk.StringVar(value=display_heuristic(self.controller.heuristic))
        self.custom_state_var = tk.StringVar(value="")
        self.speed_var = tk.IntVar(value=PLAYBACK_SPEED_DEFAULT)
        self.step_var = tk.StringVar(value=self.controller.step_label())
        self.source_var = tk.StringVar(value=self.controller.source_text())
        self.run_var = tk.StringVar(value=self.controller.run_text())

        self.tile_labels = []
        self.metric_values = {}

        self._build_layout()
        self.refresh_view()

    def _build_layout(self):
        shell = ttk.Frame(self.root, style="App.TFrame", padding=18)
        shell.pack(fill="both", expand=True)

        rail = ttk.Frame(shell, style="Rail.TFrame", width=252, padding=18)
        rail.pack(side="left", fill="y")
        rail.pack_propagate(False)

        workspace = ttk.Frame(shell, style="App.TFrame")
        workspace.pack(side="left", fill="both", expand=True, padx=(16, 0))

        topbar = tk.Frame(workspace, bg="#fcfaf6", bd=1, relief="solid", highlightthickness=0)
        topbar.pack(fill="x")

        topbar_left = tk.Frame(topbar, bg="#fcfaf6")
        topbar_left.pack(side="left", padx=18, pady=14)
        tk.Label(
            topbar_left,
            text="N-Puzzle Solver",
            bg="#fcfaf6",
            fg="#201b16",
            font=("Helvetica", 18, "bold"),
        ).pack(anchor="w")
        ttk.Label(topbar_left, textvariable=self.source_var, style="Meta.TLabel").pack(anchor="w", pady=(4, 0))

        topbar_right = tk.Frame(topbar, bg="#fcfaf6")
        topbar_right.pack(side="right", padx=18, pady=14)
        ttk.Label(topbar_right, textvariable=self.run_var, style="Meta.TLabel").pack(anchor="e")
        ttk.Label(topbar_right, textvariable=self.step_var, style="Meta.TLabel").pack(anchor="e", pady=(4, 0))

        body = ttk.Frame(workspace, style="App.TFrame")
        body.pack(fill="both", expand=True, pady=(16, 0))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        board_panel = tk.Frame(body, bg="#fcfaf6", bd=1, relief="solid", highlightthickness=0)
        board_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        detail_panel = tk.Frame(body, bg="#fcfaf6", bd=1, relief="solid", highlightthickness=0)
        detail_panel.grid(row=0, column=1, sticky="nsew")

        ttk.Label(rail, text="Controls", style="Section.TLabel").pack(anchor="w")
        ttk.Label(rail, text="Preset case", style="Rail.TLabel").pack(anchor="w", pady=(18, 4))
        case_box = ttk.Combobox(
            rail,
            textvariable=self.case_var,
            values=sorted(PRESET_CASES),
            state="readonly",
            style="App.TCombobox",
        )
        case_box.pack(fill="x")
        case_box.bind("<<ComboboxSelected>>", self.on_case_changed)

        ttk.Label(rail, text="Algorithm", style="Rail.TLabel").pack(anchor="w", pady=(14, 4))
        algorithm_box = ttk.Combobox(
            rail,
            textvariable=self.algorithm_var,
            values=[display_algorithm(name) for name in ["astar", "idastar", "bfs", "iddfs"]],
            state="readonly",
            style="App.TCombobox",
        )
        algorithm_box.pack(fill="x")
        algorithm_box.bind("<<ComboboxSelected>>", self.on_algorithm_changed)

        ttk.Label(rail, text="Heuristic", style="Rail.TLabel").pack(anchor="w", pady=(14, 4))
        heuristic_box = ttk.Combobox(
            rail,
            textvariable=self.heuristic_var,
            values=[display_heuristic(name) for name in ["linear_conflict", "manhattan"]],
            state="readonly",
            style="App.TCombobox",
        )
        heuristic_box.pack(fill="x")
        heuristic_box.bind("<<ComboboxSelected>>", self.on_heuristic_changed)

        ttk.Label(rail, text="Custom state", style="Rail.TLabel").pack(anchor="w", pady=(14, 4))
        custom_entry = ttk.Entry(rail, textvariable=self.custom_state_var, style="App.TEntry")
        custom_entry.pack(fill="x")

        ActionButton(
            rail,
            text="Load custom",
            command=self.on_custom_state,
            bg=BUTTON_DARK_BG,
            fg=BUTTON_DARK_FG,
            active_bg=BUTTON_DARK_ACTIVE_BG,
        ).pack(fill="x", pady=(8, 0))

        ttk.Label(rail, text="Playback speed (ms)", style="Rail.TLabel").pack(anchor="w", pady=(18, 4))
        speed = ttk.Scale(
            rail,
            from_=100,
            to=1200,
            orient="horizontal",
            variable=self.speed_var,
        )
        speed.pack(fill="x")

        rail_buttons = tk.Frame(rail, bg="#ebe4d7")
        rail_buttons.pack(fill="x", pady=(18, 0))
        rail_buttons.columnconfigure((0, 1), weight=1)

        for column, (label, command) in enumerate(
            [
                ("Solve", self.on_solve),
                ("Reset", self.on_reset),
            ]
        ):
            button = ActionButton(
                rail_buttons,
                text=label,
                command=command,
                bg=BUTTON_DARK_BG,
                fg=BUTTON_DARK_FG,
                active_bg=BUTTON_DARK_ACTIVE_BG,
                font=("Helvetica", 11, "bold"),
            )
            button.grid(row=0, column=column, sticky="ew", padx=(0, 4) if column == 0 else (4, 0))

        playback = tk.Frame(rail, bg="#ebe4d7")
        playback.pack(fill="x", pady=(12, 0))
        playback.columnconfigure((0, 1, 2), weight=1)

        for column, (label, command) in enumerate(
            [
                ("Prev", self.on_prev),
                ("Play", self.on_play),
                ("Next", self.on_next),
            ]
        ):
            button = ActionButton(
                playback,
                text=label,
                command=command,
                bg=BUTTON_DARK_BG,
                fg=BUTTON_DARK_FG,
                active_bg=BUTTON_DARK_ACTIVE_BG,
                padx=8,
                pady=8,
                font=("Helvetica", 10, "bold"),
            )
            button.grid(row=0, column=column, sticky="ew", padx=4 if column == 1 else (0 if column == 0 else 4, 0))

        rail_footer = tk.Label(
            rail,
            text="Run the solver, then step through the path or play it end to end.",
            bg="#ebe4d7",
            fg="#5a5146",
            justify="left",
            wraplength=208,
            font=("Helvetica", 11),
        )
        rail_footer.pack(side="bottom", anchor="w")

        board_header = tk.Frame(board_panel, bg="#fcfaf6")
        board_header.pack(fill="x", padx=18, pady=(18, 8))
        tk.Label(
            board_header,
            text="Board",
            bg="#fcfaf6",
            fg="#201b16",
            font=("Helvetica", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            board_header,
            text="Follow the returned path one position at a time.",
            bg="#fcfaf6",
            fg="#5a5146",
            font=("Helvetica", 11),
        ).pack(anchor="w", pady=(4, 0))

        grid = tk.Frame(board_panel, bg="#fcfaf6")
        grid.pack(expand=True, pady=(8, 24))

        for row in range(3):
            grid.rowconfigure(row, weight=1)
            grid.columnconfigure(row, weight=1)

        for row in range(3):
            label_row = []
            for col in range(3):
                tile = tk.Label(
                    grid,
                    width=5,
                    height=2,
                    font=("Helvetica", 30, "bold"),
                    relief="solid",
                    borderwidth=1,
                    bg="#f2eadf",
                    fg="#201b16",
                )
                tile.grid(row=row, column=col, padx=7, pady=7, sticky="nsew")
                label_row.append(tile)
            self.tile_labels.append(label_row)

        metrics_header = tk.Frame(detail_panel, bg="#fcfaf6")
        metrics_header.pack(fill="x", padx=18, pady=(18, 8))
        tk.Label(
            metrics_header,
            text="Run details",
            bg="#fcfaf6",
            fg="#201b16",
            font=("Helvetica", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            metrics_header,
            text="Metrics update after each solve. Playback controls do not rerun search.",
            bg="#fcfaf6",
            fg="#5a5146",
            font=("Helvetica", 11),
            wraplength=260,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        step_banner = tk.Label(
            detail_panel,
            textvariable=self.step_var,
            bg="#e7dece",
            fg="#201b16",
            font=("Helvetica", 12, "bold"),
            padx=12,
            pady=8,
            relief="solid",
            borderwidth=1,
        )
        step_banner.pack(fill="x", padx=18, pady=(0, 12))

        metrics = tk.Frame(detail_panel, bg="#fcfaf6")
        metrics.pack(fill="x", padx=18)

        for index, (name, value) in enumerate(self.controller.metrics()):
            tk.Label(
                metrics,
                text=name,
                bg="#fcfaf6",
                fg="#5a5146",
                font=("Helvetica", 11),
            ).grid(row=index, column=0, sticky="w", pady=4)
            value_label = tk.Label(
                metrics,
                text=value,
                bg="#fcfaf6",
                fg="#201b16",
                font=("Helvetica", 11, "bold"),
            )
            value_label.grid(row=index, column=1, sticky="e", padx=(16, 0), pady=4)
            self.metric_values[name] = value_label
        metrics.columnconfigure(1, weight=1)

        moves_panel = tk.Frame(detail_panel, bg="#fcfaf6")
        moves_panel.pack(fill="both", expand=True, padx=18, pady=(16, 18))
        tk.Label(
            moves_panel,
            text="Move sequence",
            bg="#fcfaf6",
            fg="#201b16",
            font=("Helvetica", 13, "bold"),
        ).pack(anchor="w")
        tk.Label(
            moves_panel,
            text="The solver output is shown exactly as returned.",
            bg="#fcfaf6",
            fg="#5a5146",
            font=("Helvetica", 11),
        ).pack(anchor="w", pady=(4, 10))

        self.move_list = tk.Label(
            moves_panel,
            text="(none)",
            bg="#f2eadf",
            fg="#201b16",
            justify="left",
            anchor="nw",
            padx=12,
            pady=12,
            wraplength=260,
            relief="solid",
            borderwidth=1,
            font=("Helvetica", 12),
        )
        self.move_list.pack(fill="both", expand=True)

    def on_case_changed(self, _event=None):
        self.controller.set_case(self.case_var.get())
        self.custom_state_var.set("")
        self.stop_playback()
        self.refresh_view()

    def on_algorithm_changed(self, _event=None):
        self.controller.set_algorithm(resolve_algorithm(self.algorithm_var.get()))
        self.refresh_view()

    def on_heuristic_changed(self, _event=None):
        self.controller.set_heuristic(resolve_heuristic(self.heuristic_var.get()))
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
        self.controller.set_algorithm(resolve_algorithm(self.algorithm_var.get()))
        self.controller.set_heuristic(resolve_heuristic(self.heuristic_var.get()))
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
        self.source_var.set(self.controller.source_text())
        self.run_var.set(self.controller.run_text())
        rows = self.controller.board_rows()
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                tile = self.tile_labels[row_index][col_index]
                if value == "0":
                    tile.configure(text="", bg="#d2c8b8")
                else:
                    tile.configure(text=value, bg="#f2eadf")

        for name, value in self.controller.metrics():
            self.metric_values[name].configure(text=value)

        self.step_var.set(self.controller.step_label())
        self.move_list.configure(text=self.controller.move_text())


def display_algorithm(name: str) -> str:
    return ALGORITHM_LABELS[name]


def display_heuristic(name: str) -> str:
    return HEURISTIC_LABELS[name]


def resolve_algorithm(label: str) -> str:
    for key, value in ALGORITHM_LABELS.items():
        if value == label:
            return key
    raise KeyError(label)


def resolve_heuristic(label: str) -> str:
    for key, value in HEURISTIC_LABELS.items():
        if value == label:
            return key
    raise KeyError(label)


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
