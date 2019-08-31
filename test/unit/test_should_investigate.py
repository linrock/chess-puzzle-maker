import unittest

from chess import Board
from chess.engine import Cp, Mate

from puzzlemaker.puzzle_finder import should_investigate

board = Board()

class TestShouldInvestigate(unittest.TestCase):

    def test_investigating_moderate_score_changes(self):
        score_changes = [
            [0, 200],
            [50, 200],
            [-50, 200],
        ]
        for a, b in score_changes:
            a = Cp(a)
            b = Cp(b)
            self.assertTrue(should_investigate(a, b, board))

    def test_investigating_major_score_changes(self):
        score_changes = [
            [0, 500],
            [100, 500],
            [100, -100],
        ]
        for a, b in score_changes:
            a = Cp(a)
            b = Cp(b)
            self.assertTrue(should_investigate(a, b, board))

    def test_investigating_even_position_to_mate(self):
        a = Cp(0)
        b = Mate(5)
        self.assertTrue(should_investigate(a, b, board))

        a = Cp(0)
        b = Mate(-5)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_minor_advantage_to_mate(self):
        a = Cp(100)
        b = Mate(5)
        self.assertTrue(should_investigate(a, b, board))

        a = Cp(-100)
        b = Mate(-5)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_major_advantage_to_getting_mated(self):
        a = Cp(700)
        b = Mate(-5)
        self.assertTrue(should_investigate(a, b, board))

        a = Cp(-700)
        b = Mate(5)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_major_advantage_to_major_disadvantage(self):
        a = Cp(700)
        b = Cp(-700)
        self.assertTrue(should_investigate(a, b, board))

        a = Cp(-700)
        b = Cp(700)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_major_advantage_to_even_position(self):
        a = Cp(700)
        b = Cp(0)
        self.assertTrue(should_investigate(a, b, board))

        a = Cp(-700)
        b = Cp(0)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_mate_threat_to_major_disadvantage(self):
        a = Mate(5)
        b = Cp(-700)
        self.assertTrue(should_investigate(a, b, board))

        a = Mate(-5)
        b = Cp(700)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_mate_threat_to_even_position(self):
        a = Mate(5)
        b = Cp(0)
        self.assertTrue(should_investigate(a, b, board))

        a = Mate(-5)
        b = Cp(0)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_mate_threat_to_getting_mated(self):
        a = Mate(1)
        b = Mate(-1)
        self.assertTrue(should_investigate(a, b, board))

        a = Mate(-1)
        b = Mate(1)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_mate_threat_to_checkmate(self):
        a = Mate(1)
        b = Mate(0)
        self.assertFalse(should_investigate(a, b, board))

    def test_not_investigating_insignificant_score_changes(self):
        score_changes = [
            [0, 0],
            [-50, 50],
            [50, -50],
            [-70, -70],
            [70, 70],
        ]
        for a, b in score_changes:
            a = Cp(a)
            b = Cp(b)
            self.assertFalse(should_investigate(a, b, board))

    def test_not_investigating_major_advantage_to_mate_threat(self):
        a = Cp(900)
        b = Mate(5)
        self.assertFalse(should_investigate(a, b, board))

        a = Cp(-900)
        b = Mate(-5)
        self.assertFalse(should_investigate(a, b, board))

    def test_not_investigating_even_position(self):
        board = Board("4k3/8/3n4/3N4/8/8/4K3/8 w - - 0 1")

        a = Cp(0)
        b = Cp(0)
        self.assertFalse(should_investigate(a, b, board))

        a = Cp(9)
        b = Cp(9)
        self.assertFalse(should_investigate(a, b, board))


if __name__ == '__main__':
    unittest.main()
