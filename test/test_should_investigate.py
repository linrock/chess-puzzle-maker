import unittest

import chess
import chess.uci

from modules.utils import should_investigate

board = chess.Board()

class TestShouldInvestigate(unittest.TestCase):

    def test_investigating_moderate_score_changes(self):
        score_changes = [
            [0, 200],
            [50, 200],
            [-50, 200],
        ]
        for a, b in score_changes:
            a = chess.uci.Score(a, None)
            b = chess.uci.Score(b, None)
            self.assertTrue(should_investigate(a, b, board))

    def test_investigating_major_score_changes(self):
        score_changes = [
            [0, 500],
            [100, 500],
            [100, -100],
        ]
        for a, b in score_changes:
            a = chess.uci.Score(a, None)
            b = chess.uci.Score(b, None)
            self.assertTrue(should_investigate(a, b, board))

    def test_investigating_even_position_to_mate(self):
        a = chess.uci.Score(0, None)
        b = chess.uci.Score(None, 5)
        self.assertTrue(should_investigate(a, b, board))

        a = chess.uci.Score(0, None)
        b = chess.uci.Score(None, -5)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_minor_advantage_to_mate(self):
        a = chess.uci.Score(100, None)
        b = chess.uci.Score(None, 5)
        self.assertTrue(should_investigate(a, b, board))

        a = chess.uci.Score(-100, None)
        b = chess.uci.Score(None, -5)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_major_advantage_to_getting_mated(self):
        a = chess.uci.Score(700, None)
        b = chess.uci.Score(None, -5)
        self.assertTrue(should_investigate(a, b, board))

        a = chess.uci.Score(-700, None)
        b = chess.uci.Score(None, 5)
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_major_advantage_to_major_disadvantage(self):
        a = chess.uci.Score(700, None)
        b = chess.uci.Score(-700, None)
        self.assertTrue(should_investigate(a, b, board))

        a = chess.uci.Score(-700, None)
        b = chess.uci.Score(700, None) 
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_major_advantage_to_even_position(self):
        a = chess.uci.Score(700, None)
        b = chess.uci.Score(0, None)
        self.assertTrue(should_investigate(a, b, board))

        a = chess.uci.Score(-700, None)
        b = chess.uci.Score(0, None) 
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_mate_threat_to_major_disadvantage(self):
        a = chess.uci.Score(None, 5)
        b = chess.uci.Score(-700, None)
        self.assertTrue(should_investigate(a, b, board))

        a = chess.uci.Score(None, -5)
        b = chess.uci.Score(700, None) 
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_mate_threat_to_even_position(self):
        a = chess.uci.Score(None, 5)
        b = chess.uci.Score(0, None)
        self.assertTrue(should_investigate(a, b, board))

        a = chess.uci.Score(None, -5)
        b = chess.uci.Score(0, None) 
        self.assertTrue(should_investigate(a, b, board))

    def test_investigating_mate_threat_to_getting_mated(self):
        a = chess.uci.Score(None, 1)
        b = chess.uci.Score(None, -1)
        self.assertTrue(should_investigate(a, b, board))

        a = chess.uci.Score(None, -1)
        b = chess.uci.Score(None, 1)
        self.assertTrue(should_investigate(a, b, board))

    def test_not_investigating_insignificant_score_changes(self):
        score_changes = [
            [0, 0],
            [-50, 50],
            [50, -50],
            [-70, -70],
            [70, 70],
        ]
        for a, b in score_changes:
            a = chess.uci.Score(a, None)
            b = chess.uci.Score(b, None)
            self.assertFalse(should_investigate(a, b, board))

    def test_not_investigating_major_advantage_to_mate_threat(self):
        a = chess.uci.Score(900, None)
        b = chess.uci.Score(None, 5)
        self.assertFalse(should_investigate(a, b, board))

        a = chess.uci.Score(-900, None)
        b = chess.uci.Score(None, -5)
        self.assertFalse(should_investigate(a, b, board))


if __name__ == '__main__':
    unittest.main()
