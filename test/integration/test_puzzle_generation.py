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
        puzzle.generate()
        self.assertFalse(puzzle.is_complete())

    def test_mate_in_3_is_complete_1(self):
        # 1. Qxh8+ Kxh8 2. Bf6+ Kg8 3. Re8#
        board = chess.Board(
            'r1b3kr/ppp1Bp1p/1b6/n2P4/2p3q1/2Q2N2/P4PPP/RN2R1K1 w - - 1 0'
        )
        puzzle = Puzzle(board, board.parse_san('Qxh8+'), chess.pgn.Game())
        puzzle.generate()
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(len(puzzle.position_list_node.move_list()) == 4)

    def test_mate_in_3_is_complete_2(self):
        # 1... Qxf2+ 2. Rxf2 Rxf2+ 3. Kh1 Ng3#
        board = chess.Board(
            'r2n1rk1/1ppb2pp/1p1p4/3Ppq1n/2B3P1/2P4P/PP1N1P1K/R2Q1RN1 b - - 0 1'
        )
        puzzle = Puzzle(board, board.parse_san('Qxf2+'), chess.pgn.Game())
        puzzle.generate()
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(len(puzzle.position_list_node.move_list()) == 4)

    def test_mate_in_3_is_complete_3(self):
        # 1. Rxh7+ Kxh7 2. Rh1+ Kg7 3. Qh6#
        board = chess.Board(
            '3q1r1k/2p4p/1p1pBrp1/p2Pp3/2PnP3/5PP1/PP1Q2K1/5R1R w - - 1 0'
        )
        puzzle = Puzzle(board, board.parse_san('Rxh7+'), chess.pgn.Game())
        puzzle.generate()
        self.assertTrue(puzzle.is_complete())
        self.assertEqual(
            puzzle.position_list_node.move_list(),
            ['h8h7', 'f1h1', 'h7g7', 'd2h6'],
        )


if __name__ == '__main__':
    unittest.main()
