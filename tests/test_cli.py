import subprocess
import sys
import unittest


class CliTests(unittest.TestCase):
    def test_solve_command_prints_stage_one_board_details(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "npuzzle.cli",
                "solve",
                "--state",
                "1 2 3 4 5 6 7 8 0",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("State is solvable: yes", result.stdout)
        self.assertIn("Goal reached: yes", result.stdout)

    def test_solve_command_runs_bfs_for_easy_case(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "npuzzle.cli",
                "solve",
                "--algorithm",
                "bfs",
                "--case",
                "easy",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Algorithm: bfs", result.stdout)
        self.assertIn("Solved: yes", result.stdout)
        self.assertIn("Move count: 1", result.stdout)

    def test_solve_command_runs_iddfs_for_easy_case(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "npuzzle.cli",
                "solve",
                "--algorithm",
                "iddfs",
                "--case",
                "easy",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Algorithm: iddfs", result.stdout)
        self.assertIn("Solved: yes", result.stdout)
        self.assertIn("Move count: 1", result.stdout)

    def test_solve_command_runs_astar_with_manhattan(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "npuzzle.cli",
                "solve",
                "--algorithm",
                "astar",
                "--heuristic",
                "manhattan",
                "--case",
                "medium",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Algorithm: astar", result.stdout)
        self.assertIn("Heuristic: manhattan", result.stdout)
        self.assertIn("Solved: yes", result.stdout)

    def test_solve_command_runs_astar_with_linear_conflict(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "npuzzle.cli",
                "solve",
                "--algorithm",
                "astar",
                "--heuristic",
                "linear_conflict",
                "--case",
                "medium",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Algorithm: astar", result.stdout)
        self.assertIn("Heuristic: linear_conflict", result.stdout)
        self.assertIn("Solved: yes", result.stdout)

    def test_solve_command_runs_idastar_with_linear_conflict(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "npuzzle.cli",
                "solve",
                "--algorithm",
                "idastar",
                "--heuristic",
                "linear_conflict",
                "--case",
                "medium",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Algorithm: idastar", result.stdout)
        self.assertIn("Heuristic: linear_conflict", result.stdout)
        self.assertIn("Solved: yes", result.stdout)

    def test_solve_command_reports_unsolvable_state_without_search(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "npuzzle.cli",
                "solve",
                "--algorithm",
                "idastar",
                "--heuristic",
                "linear_conflict",
                "--state",
                "1 2 3 4 5 6 8 7 0",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Solved: no", result.stdout)
        self.assertIn("Nodes expanded: 0", result.stdout)

    def test_benchmark_command_prints_all_algorithms(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "npuzzle.cli",
                "benchmark",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Case", result.stdout)
        self.assertIn("Algorithm", result.stdout)
        self.assertIn("bfs", result.stdout)
        self.assertIn("iddfs", result.stdout)
        self.assertIn("astar", result.stdout)
        self.assertIn("idastar", result.stdout)


if __name__ == "__main__":
    unittest.main()
