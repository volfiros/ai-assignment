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


if __name__ == "__main__":
    unittest.main()
