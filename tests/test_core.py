import unittest

from npuzzle.core import (
    GOAL_STATE,
    format_state,
    get_neighbors,
    is_goal,
    is_solvable,
    parse_state,
)
from npuzzle.presets import PRESET_CASES


class ParseStateTests(unittest.TestCase):
    def test_parse_state_accepts_space_separated_tiles(self):
        self.assertEqual(parse_state("1 2 3 4 5 6 7 8 0"), GOAL_STATE)

    def test_parse_state_rejects_duplicate_tiles(self):
        with self.assertRaises(ValueError):
            parse_state("1 2 3 4 5 6 7 7 0")

    def test_format_state_renders_three_rows(self):
        self.assertEqual(format_state(GOAL_STATE), "1 2 3\n4 5 6\n7 8 0")


class NeighborTests(unittest.TestCase):
    def test_corner_blank_has_two_neighbors(self):
        neighbors = get_neighbors((0, 1, 2, 3, 4, 5, 6, 7, 8))
        self.assertEqual({move for move, _ in neighbors}, {"down", "right"})

    def test_edge_blank_has_three_neighbors(self):
        neighbors = get_neighbors((1, 0, 2, 3, 4, 5, 6, 7, 8))
        self.assertEqual({move for move, _ in neighbors}, {"down", "left", "right"})

    def test_center_blank_has_four_neighbors(self):
        neighbors = get_neighbors((1, 2, 3, 4, 0, 5, 6, 7, 8))
        self.assertEqual({move for move, _ in neighbors}, {"down", "left", "right", "up"})


class SolvabilityTests(unittest.TestCase):
    def test_goal_state_is_solvable(self):
        self.assertTrue(is_solvable(GOAL_STATE))

    def test_unsolvable_state_is_rejected(self):
        self.assertFalse(is_solvable((1, 2, 3, 4, 5, 6, 8, 7, 0)))

    def test_presets_include_easy_medium_and_hard(self):
        self.assertEqual(set(PRESET_CASES), {"easy", "medium", "hard"})
        self.assertTrue(all(is_solvable(state) for state in PRESET_CASES.values()))

    def test_goal_detection(self):
        self.assertTrue(is_goal(GOAL_STATE))
        self.assertFalse(is_goal(PRESET_CASES["easy"]))


if __name__ == "__main__":
    unittest.main()
