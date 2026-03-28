import subprocess
import sys
import unittest

from npuzzle.app import PuzzleController
from npuzzle.presets import PRESET_CASES


class PuzzleControllerTests(unittest.TestCase):
    def test_controller_uses_medium_astar_defaults(self):
        controller = PuzzleController()

        self.assertEqual(controller.selected_case, "medium")
        self.assertEqual(controller.algorithm, "astar")
        self.assertEqual(controller.heuristic, "linear_conflict")
        self.assertEqual(controller.current_state, PRESET_CASES["medium"])

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


if __name__ == "__main__":
    unittest.main()
