import unittest

from npuzzle.core import GOAL_STATE
from npuzzle.heuristics import linear_conflict, manhattan_distance


class ManhattanDistanceTests(unittest.TestCase):
    def test_goal_state_has_zero_cost(self):
        self.assertEqual(manhattan_distance(GOAL_STATE), 0)

    def test_known_board_has_expected_manhattan_cost(self):
        state = (1, 2, 3, 4, 5, 6, 0, 7, 8)
        self.assertEqual(manhattan_distance(state), 2)


class LinearConflictTests(unittest.TestCase):
    def test_linear_conflict_matches_goal_cost(self):
        self.assertEqual(linear_conflict(GOAL_STATE), 0)

    def test_linear_conflict_dominates_manhattan_on_conflict_board(self):
        state = (2, 1, 3, 4, 5, 6, 8, 7, 0)
        self.assertEqual(manhattan_distance(state), 4)
        self.assertEqual(linear_conflict(state), 8)


if __name__ == "__main__":
    unittest.main()
