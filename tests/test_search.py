import unittest

from npuzzle.core import GOAL_STATE
from npuzzle.search import SearchResult, solve_bfs, solve_iddfs


class BfsTests(unittest.TestCase):
    def test_bfs_solves_easy_board_in_one_move(self):
        result = solve_bfs((1, 2, 3, 4, 5, 6, 7, 0, 8))

        self.assertIsInstance(result, SearchResult)
        self.assertTrue(result.solved)
        self.assertEqual(result.path, [(1, 2, 3, 4, 5, 6, 7, 0, 8), GOAL_STATE])
        self.assertEqual(result.moves, ["right"])
        self.assertEqual(result.algorithm, "bfs")
        self.assertIsNone(result.heuristic)
        self.assertGreaterEqual(result.nodes_generated, 1)


class IddfsTests(unittest.TestCase):
    def test_iddfs_matches_bfs_solution_length_on_easy_board(self):
        bfs_result = solve_bfs((1, 2, 3, 4, 5, 6, 7, 0, 8))
        iddfs_result = solve_iddfs((1, 2, 3, 4, 5, 6, 7, 0, 8))

        self.assertTrue(iddfs_result.solved)
        self.assertEqual(len(iddfs_result.moves), len(bfs_result.moves))
        self.assertEqual(iddfs_result.moves, ["right"])
        self.assertEqual(iddfs_result.algorithm, "iddfs")
        self.assertIsNone(iddfs_result.heuristic)
        self.assertGreaterEqual(iddfs_result.nodes_expanded, 1)

    def test_iddfs_returns_zero_move_solution_for_goal(self):
        result = solve_iddfs(GOAL_STATE)

        self.assertTrue(result.solved)
        self.assertEqual(result.path, [GOAL_STATE])
        self.assertEqual(result.moves, [])


if __name__ == "__main__":
    unittest.main()
