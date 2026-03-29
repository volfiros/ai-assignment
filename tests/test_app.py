import subprocess
import sys
import tkinter as tk
import unittest

from npuzzle.app import (
    ActionButton,
    ALGORITHM_LABELS,
    BUTTON_DARK_BG,
    BUTTON_DARK_FG,
    HEURISTIC_LABELS,
    PLAYBACK_SPEED_DEFAULT,
    PuzzleController,
    display_algorithm,
    display_heuristic,
    resolve_algorithm,
    resolve_heuristic,
)
from npuzzle.presets import PRESET_CASES


class PuzzleControllerTests(unittest.TestCase):
    def test_controller_uses_medium_astar_defaults(self):
        controller = PuzzleController()

        self.assertEqual(controller.selected_case, "medium")
        self.assertEqual(controller.algorithm, "astar")
        self.assertEqual(controller.heuristic, "linear_conflict")
        self.assertEqual(controller.current_state, PRESET_CASES["medium"])
        self.assertEqual(controller.run_text(), "A* • Linear Conflict")

    def test_controller_solves_easy_case_and_tracks_steps(self):
        controller = PuzzleController()
        controller.set_case("easy")
        result = controller.solve()

        self.assertTrue(result.solved)
        self.assertEqual(result.moves, ["right"])
        self.assertEqual(controller.current_state, PRESET_CASES["easy"])
        self.assertEqual(controller.step_label(), "Step 1/2")

        controller.next_step()
        self.assertEqual(controller.current_state, result.path[-1])
        self.assertEqual(controller.step_label(), "Step 2/2")

    def test_reset_restores_selected_case_and_clears_result(self):
        controller = PuzzleController()
        controller.set_case("easy")
        controller.solve()
        controller.next_step()

        controller.reset()

        self.assertEqual(controller.current_state, PRESET_CASES["easy"])
        self.assertIsNone(controller.result)
        self.assertEqual(controller.step_label(), "Step 1/1")

    def test_custom_state_updates_board(self):
        controller = PuzzleController()
        controller.set_custom_state("1 2 3 4 5 6 7 0 8")

        self.assertEqual(controller.selected_case, "custom")
        self.assertEqual(controller.current_state, (1, 2, 3, 4, 5, 6, 7, 0, 8))

    def test_unsolvable_solve_returns_zero_work_result(self):
        controller = PuzzleController()
        controller.set_algorithm("idastar")
        controller.set_custom_state("1 2 3 4 5 6 8 7 0")
        result = controller.solve()

        self.assertFalse(result.solved)
        self.assertEqual(result.nodes_expanded, 0)
        self.assertEqual(controller.step_label(), "Step 1/1")

    def test_move_text_formats_solution_path_for_ui(self):
        controller = PuzzleController()
        controller.set_case("easy")
        controller.solve()

        self.assertEqual(controller.move_text(), "right")
        controller.reset()
        self.assertEqual(controller.move_text(), "(none)")


class AppSmokeTests(unittest.TestCase):
    def test_smoke_test_mode_exits_cleanly(self):
        result = subprocess.run(
            [sys.executable, "-m", "npuzzle.app", "--smoke-test"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("N-Puzzle visualizer ready", result.stdout)


class AppStyleTests(unittest.TestCase):
    def test_secondary_buttons_use_high_contrast_palette(self):
        self.assertEqual(BUTTON_DARK_BG, "#30271e")
        self.assertEqual(BUTTON_DARK_FG, "#f8f4ed")

    def test_action_buttons_use_label_based_rendering(self):
        self.assertTrue(issubclass(ActionButton, tk.Label))

    def test_playback_speed_default_is_six_hundred(self):
        self.assertEqual(PLAYBACK_SPEED_DEFAULT, 600)

    def test_display_labels_are_human_readable(self):
        self.assertEqual(ALGORITHM_LABELS["astar"], "A*")
        self.assertEqual(ALGORITHM_LABELS["bfs"], "BFS")
        self.assertEqual(HEURISTIC_LABELS["linear_conflict"], "Linear Conflict")
        self.assertEqual(display_algorithm("idastar"), "IDA*")
        self.assertEqual(display_heuristic("manhattan"), "Manhattan")

    def test_selection_helpers_map_labels_back_to_internal_keys(self):
        self.assertEqual(resolve_algorithm("A*"), "astar")
        self.assertEqual(resolve_heuristic("Linear Conflict"), "linear_conflict")


if __name__ == "__main__":
    unittest.main()
