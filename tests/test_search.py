import unittest

from npuzzle.core import GOAL_STATE
from npuzzle.search import SearchResult, solve_astar, solve_bfs, solve_idastar, solve_iddfs


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


class AStarTests(unittest.TestCase):
    def test_astar_matches_bfs_solution_length_on_medium_board(self):
        state = (1, 2, 3, 5, 0, 6, 4, 7, 8)
        bfs_result = solve_bfs(state)
        astar_result = solve_astar(state, "manhattan")

        self.assertTrue(astar_result.solved)
        self.assertEqual(len(astar_result.moves), len(bfs_result.moves))
        self.assertEqual(astar_result.algorithm, "astar")
        self.assertEqual(astar_result.heuristic, "manhattan")

    def test_linear_conflict_expands_no_more_nodes_than_manhattan(self):
        state = (2, 1, 3, 4, 5, 6, 8, 7, 0)
        manhattan_result = solve_astar(state, "manhattan")
        linear_conflict_result = solve_astar(state, "linear_conflict")

        self.assertTrue(manhattan_result.solved)
        self.assertTrue(linear_conflict_result.solved)
        self.assertLessEqual(
            linear_conflict_result.nodes_expanded,
            manhattan_result.nodes_expanded,
        )
        self.assertEqual(linear_conflict_result.heuristic, "linear_conflict")


class IdaStarTests(unittest.TestCase):
    def test_idastar_matches_astar_solution_length_on_medium_board(self):
        state = (1, 2, 3, 5, 0, 6, 4, 7, 8)
        astar_result = solve_astar(state, "linear_conflict")
        idastar_result = solve_idastar(state, "linear_conflict")

        self.assertTrue(idastar_result.solved)
        self.assertEqual(len(idastar_result.moves), len(astar_result.moves))
        self.assertEqual(idastar_result.algorithm, "idastar")
        self.assertEqual(idastar_result.heuristic, "linear_conflict")


class UnsolvableTests(unittest.TestCase):
    def test_all_solvers_short_circuit_unsolvable_state(self):
        state = (1, 2, 3, 4, 5, 6, 8, 7, 0)

        results = [
            solve_bfs(state),
            solve_iddfs(state),
            solve_astar(state, "manhattan"),
            solve_idastar(state, "linear_conflict"),
        ]

        for result in results:
            self.assertFalse(result.solved)
            self.assertEqual(result.path, [])
            self.assertEqual(result.moves, [])
            self.assertEqual(result.nodes_expanded, 0)
            self.assertEqual(result.nodes_generated, 0)
            self.assertEqual(result.max_frontier, 0)


if __name__ == "__main__":
    unittest.main()
