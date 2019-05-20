import io
import unittest

import chess
import chess.pgn

from modules.puzzle import Puzzle

# import sys
# import logging

# logging.basicConfig(format="%(message)s", level=logging.DEBUG, stream=sys.stdout)
# logging.getLogger("chess").setLevel(logging.WARNING)

SEARCH_DEPTH = 12


class TestPuzzleIsComplete(unittest.TestCase):

    def test_puzzle_is_not_complete(self):
        board = chess.Board()
        puzzle = Puzzle(board, chess.Move.from_uci("e2e4"))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertFalse(puzzle.is_complete())

    def test_bishop_fork(self):
        # source game https://lichess.org/1n12OmvV
        # 34. Rb7
        board = chess.Board(
            '6k1/R4p2/1r3npp/2N5/P1b2P2/6P1/3r2BP/4R1K1 w - - 0 34'
        )
        puzzle = Puzzle(board, board.parse_san('Rb7'))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.category() == "Material")
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions][:6],
            ['a7b7', 'd2g2', 'g1g2', 'c4d5', 'g2g1', 'd5b7'],
        )

    def test_mate_in_3_is_complete_1(self):
        # 1. Qxh8+ Kxh8 2. Bf6+ Kg8 3. Re8#
        board = chess.Board(
            'r1b3kr/ppp1Bp1p/1b6/n2P4/2p3q1/2Q2N2/P4PPP/RN2R1K1 w - - 1 0'
        )
        puzzle = Puzzle(board, board.parse_san('Qxh8+'))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.category() == "Mate")
        self.assertTrue(len(puzzle.positions) == 5)
        # game = chess.pgn.read_game(io.StringIO(str(puzzle.to_pgn())))
        # moves1 = [m for m in game.mainline_moves()]

    def test_mate_in_3_is_complete_2(self):
        # 1... Qxf2+ 2. Rxf2 Rxf2+ 3. Kh1 Ng3#
        board = chess.Board(
            'r2n1rk1/1ppb2pp/1p1p4/3Ppq1n/2B3P1/2P4P/PP1N1P1K/R2Q1RN1 b - - 0 1'
        )
        puzzle = Puzzle(board, board.parse_san('Qxf2+'))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.category() == "Mate")
        self.assertTrue(len(puzzle.positions) == 5)

    def test_mate_in_3_is_complete_3(self):
        # 1. Rxh7+ Kxh7 2. Rh1+ Kg7 3. Qh6#
        board = chess.Board(
            '3q1r1k/2p4p/1p1pBrp1/p2Pp3/2PnP3/5PP1/PP1Q2K1/5R1R w - - 1 0'
        )
        puzzle = Puzzle(board, board.parse_san('Rxh7+'))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions],
            ['h1h7', 'h8h7', 'f1h1', 'h7g7', 'd2h6'],
        )
        self.assertTrue(puzzle.category() == "Mate")
        self.assertTrue(puzzle.is_complete())

    def test_threefold_repetition_detection(self):
        # https://lichess.org/tYLGlqsX
        # 21... Be6??
        board = chess.Board(
            'r1b2r1k/ppp2p1p/8/P3p2p/2PqP3/3P1Q1P/6PK/5R2 b - - 3 21'
        )
        puzzle = Puzzle(board, board.parse_san('Be6'))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertTrue(puzzle.is_complete())
        # test that the puzzle stops at a threefold repetition position
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions],
            ['c8e6', 'f3f6', 'h8g8', 'f6g5', 'g8h8', 'g5f6', 'h8g8', 'f6g5', 'g8h8'],
        )
 

if __name__ == '__main__':
    unittest.main()
