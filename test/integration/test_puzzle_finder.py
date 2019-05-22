import io
import os
import unittest

import chess.pgn

from modules.puzzle_finder import find_puzzle_candidates
from modules.analysis import engine


def pgn_file_path(pgn_filename) -> io.TextIOWrapper:
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    return open(os.path.join(cur_dir, '..', 'fixtures', pgn_filename))


class TestPuzzleFinder(unittest.TestCase):

    def test_finding_blunder(self):
        with pgn_file_path("carlsen-anand-blunder.wc2014.pgn") as f:
            game = chess.pgn.read_game(f)
        puzzles = find_puzzle_candidates(game, scan_depth=12)
        found_blunder = False
        fen = '6rr/1k3p2/1pb1p1np/p1p1P2R/2P3R1/2P1B3/P1B2PP1/2K5 w - - 4 26'
        move = 'c1d2'
        for puzzle in puzzles:
            if (puzzle.initial_board.fen() == fen
                and puzzle.initial_move.uci() == move):
                found_blunder = True
        self.assertTrue(found_blunder)
