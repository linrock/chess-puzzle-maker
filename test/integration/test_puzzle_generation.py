import unittest

import chess
import chess.pgn

from modules.puzzle import Puzzle

class TestPuzzleIsComplete(unittest.TestCase):

    def test_puzzle_is_not_complete(self):
        board = chess.Board()
        puzzle = Puzzle(
            board,
            chess.Move.from_uci("e2e4"),
            chess.pgn.Game(),
            False,
        )
        puzzle.generate()
        self.assertFalse(puzzle.is_complete())

    def test_mate_in_3_is_complete(self):
        # 1. Rxh7+ Kxh7 2. Rh1+ Kg7 3. Qh6#
        board = chess.Board(
            '3q1r1k/2p4p/1p1pBrp1/p2Pp3/2PnP3/5PP1/PP1Q2K1/5R1R w - - 1 0'
        )
        puzzle = Puzzle(
            board,
            board.parse_san('Rxh7+'),
            chess.pgn.Game(),
            False,
        )
        puzzle.generate()
        self.assertTrue(puzzle.is_complete())


if __name__ == '__main__':
    unittest.main()
