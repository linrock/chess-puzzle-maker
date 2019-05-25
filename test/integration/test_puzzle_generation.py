import io
import os
import unittest

import chess
import chess.pgn

from modules.puzzle import Puzzle
from modules.analysis import AnalysisEngine

# from modules.logger import configure_logging
# configure_logging()

# use a lower search depth when possible for faster tests
SEARCH_DEPTH = 12


def pgn_file_path(pgn_filename) -> io.TextIOWrapper:
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    return open(os.path.join(cur_dir, '..', 'fixtures', pgn_filename))


class TestPuzzleIsComplete(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        AnalysisEngine.instance()

    @classmethod
    def tearDownClass(self):
        AnalysisEngine.quit()

    def test_puzzle_is_not_complete(self):
        board = chess.Board()
        puzzle = Puzzle(board, chess.Move.from_uci("e2e4"))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertFalse(puzzle.is_complete())

    def test_bishop_fork(self):
        # source https://lichess.org/training/61079
        # source game https://lichess.org/1n12OmvV
        # 34. Rb7
        board = chess.Board(
            '6k1/R4p2/1r3npp/2N5/P1b2P2/6P1/3r2BP/4R1K1 w - - 0 34'
        )
        puzzle = Puzzle(board, board.parse_san('Rb7'))
        puzzle.generate(depth=15)
        self.assertTrue(puzzle.is_complete())
        self.assertFalse(puzzle.player_moves_first)
        self.assertEqual(puzzle.category(), "Material")
        expected_uci_moves = ['a7b7', 'd2g2', 'g1g2', 'c4d5', 'g2g1', 'd5b7']
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions][:6],
            expected_uci_moves
        )
        game = chess.pgn.read_game(io.StringIO(puzzle.to_pgn()))
        self.assertEqual(
            [m.uci() for m in game.mainline_moves()][:6],
            expected_uci_moves
        )

    def test_mate_in_3_is_complete_1(self):
        # 1. Qxh8+ Kxh8 2. Bf6+ Kg8 3. Re8#
        board = chess.Board(
            'r1b3kr/ppp1Bp1p/1b6/n2P4/2p3q1/2Q2N2/P4PPP/RN2R1K1 w - - 1 0'
        )
        puzzle = Puzzle(board)
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.player_moves_first)
        self.assertEqual(puzzle.category(), "Mate")
        # self.assertTrue(len(puzzle.positions) == 5)
        expected_uci_moves = ['c3h8', 'g8h8', 'e7f6']
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions][:3],
            expected_uci_moves
        )
        game = chess.pgn.read_game(io.StringIO(puzzle.to_pgn()))
        self.assertEqual(
            [m.uci() for m in game.mainline_moves()][:3],
            expected_uci_moves
        )

    def test_mate_in_3_is_complete_2(self):
        # 1... Qxf2+ 2. Rxf2 Rxf2+ 3. Kh1 Ng3#
        board = chess.Board(
            'r2n1rk1/1ppb2pp/1p1p4/3Ppq1n/2B3P1/2P4P/PP1N1P1K/R2Q1RN1 b - - 0 1'
        )
        puzzle = Puzzle(board, board.parse_san('Qxf2+'))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertTrue(puzzle.player_moves_first)
        self.assertEqual(puzzle.category(), "Mate")
        # self.assertTrue(puzzle.is_complete())
        # self.assertTrue(len(puzzle.positions) == 5)

    def test_mate_in_3_is_complete_3(self):
        # 1. Rxh7+ Kxh7 2. Rh1+ Kg7 3. Qh6#
        board = chess.Board(
            '3q1r1k/2p4p/1p1pBrp1/p2Pp3/2PnP3/5PP1/PP1Q2K1/5R1R w - - 1 0'
        )
        puzzle = Puzzle(board, board.parse_san('Rxh7+'))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.player_moves_first)
        self.assertEqual(puzzle.category(), "Mate")
        expected_uci_moves = ['h1h7', 'h8h7', 'f1h1', 'h7g7', 'd2h6']
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions],
            expected_uci_moves
        )
        game = chess.pgn.read_game(io.StringIO(puzzle.to_pgn()))
        self.assertEqual(
            [m.uci() for m in game.mainline_moves()][:5],
            expected_uci_moves
        )

    def test_threefold_repetition_detection(self):
        # https://lichess.org/tYLGlqsX
        # 21... Be6??
        board = chess.Board(
            'r1b2r1k/ppp2p1p/8/P3p2p/2PqP3/3P1Q1P/6PK/5R2 b - - 3 21'
        )
        puzzle = Puzzle(board, board.parse_san('Be6'))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertTrue(puzzle.is_complete())
        self.assertFalse(puzzle.player_moves_first)
        self.assertEqual(puzzle.category(), "Equalize")
        # test that the puzzle stops at a threefold repetition position
        expected_uci_moves = [
            'c8e6', 'f3f6', 'h8g8', 'f6g5', 'g8h8', 'g5f6', 'h8g8', 'f6g5', 'g8h8'
        ]
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions],
            expected_uci_moves
        )
        game = chess.pgn.read_game(io.StringIO(puzzle.to_pgn()))
        self.assertEqual(
            [m.uci() for m in game.mainline_moves()],
            expected_uci_moves
        )
 
    def test_puzzles_without_initial_move(self):
        depth = 14

        # https://www.chesstactics.org/removing-the-guard
        # Figure 5.1.1.1
        board = chess.Board(
            '3rr1k1/ppq2pp1/2p1b2p/8/3P2n1/2N3P1/PP3PBP/R2QR1K1 w - - 0 1'
        )
        puzzle = Puzzle(board)
        puzzle.generate(depth=depth)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.player_moves_first)
        self.assertEqual(puzzle.category(), "Material")

        # Figure 5.1.1.2
        board = chess.Board(
            '1k6/p7/1p1prrB1/7P/4R3/2P3K1/PP3P2/8 b - - 0 1'
        )
        puzzle = Puzzle(board)
        puzzle.generate(depth=depth)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.player_moves_first)
        self.assertEqual(puzzle.category(), "Material")
        expected_uci_moves = [
            'f6g6', 'h5g6', 'e6e4', 'f2f4'
        ]
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions],
            expected_uci_moves
        )

        # Figure 5.1.1.3
        board = chess.Board(
            '8/1p6/p3pk2/5nR1/8/P3rN2/1P3KP1/8 w - - 0 1'
        )
        puzzle = Puzzle(board)
        puzzle.generate(depth=depth)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.category() == "Material")
        self.assertTrue(puzzle.player_moves_first)
        expected_uci_moves = [
            'g5f5', 'f6f5', 'f2e3'
        ]
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions[:3]],
            expected_uci_moves
        )

        # Figure 5.4.1.2
        board = chess.Board(
            '6rk/p3qp2/1np5/2b1pP2/4P1nr/1BN2Q2/PP3P2/3R1K1R w - - 0 1'
        )
        puzzle = Puzzle(board)
        puzzle.generate(depth=depth)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.category() == "Material")
        self.assertTrue(puzzle.player_moves_first)
        expected_uci_moves = [
            'f5f6', 'e7f6', 'f3f6', 'g4f6', 'h1h4', 'h8g7'
        ]
        self.assertEqual(
            [str(p.initial_move) for p in puzzle.positions],
            expected_uci_moves
        )

        # http://wtharvey.com/a01.html
        # Juan Bellon Lopez vs Ljubomir Ljubojevic, Palma de Majorca, 1972
        board = chess.Board(
            'r2qr3/2pp1pkp/b1p3p1/p7/P7/1PnBPQ2/2PN1PPP/R4RK1 w - - 0 1'
        )
        puzzle = Puzzle(board)
        puzzle.generate(depth=14)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.category() == "Material")
        self.assertTrue(puzzle.player_moves_first)

    def test_puzzles_loaded_from_pgn(self):
        with pgn_file_path("wtharvey.pgn") as f:
            game = chess.pgn.read_game(f)
        puzzle = Puzzle(game.board())
        puzzle.generate(depth=14)
        self.assertTrue(puzzle.is_complete())
        self.assertTrue(puzzle.category() == "Material")
        self.assertTrue(puzzle.player_moves_first)
        self.assertEqual(
            [m.uci() for m in game.mainline_moves()],
            [str(p.initial_move) for p in puzzle.positions],
        )

    def test_crash(self):
        board = chess.Board(
            '8/p6P/R7/2q5/1p1b4/1kp5/5PP1/3Q2K1 b - - 9 44'
        )
        puzzle = Puzzle(board, board.parse_san('Kc4'))
        puzzle.generate(depth=SEARCH_DEPTH)
        self.assertFalse(puzzle.is_complete())
        self.assertTrue(puzzle.category() == "Mate")


if __name__ == '__main__':
    unittest.main()
