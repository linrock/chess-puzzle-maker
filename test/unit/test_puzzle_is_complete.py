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
        )
        self.assertFalse(puzzle.is_complete())


if __name__ == '__main__':
    unittest.main()
