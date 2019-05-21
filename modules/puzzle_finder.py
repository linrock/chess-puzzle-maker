import logging
from typing import List

from chess.pgn import Game
from chess.engine import Cp, Limit

from modules.logger import log_move
from modules.bcolors import bcolors
from modules.utils import should_investigate
from modules.puzzle import Puzzle
from modules.analysis import engine


def find_puzzle_candidates(game, scan_depth=16) -> List[Puzzle]:
    """ finds puzzle candidates from a chess game 
    """
    logging.debug(
        bcolors.DIM +
        ("Scanning game for puzzles (depth: %d)..." % scan_depth) +
        bcolors.ENDC
    )
    prev_score = Cp(0)
    puzzles = []
    i = 0
    node = game
    while not node.is_end():
        next_node = node.variation(0)
        next_board = next_node.board()
        info = engine.analyse(next_board, Limit(depth=scan_depth))
        cur_score = info["score"].white()
        board = node.board()
        highlight_move = False
        if should_investigate(prev_score, cur_score, board):
            highlight_move = True
            # Found a possible puzzle
            # don't check for move ambiguity if it's the first position in
            # the PGN since the PGN might be a puzzle instead of a game
            puzzle = Puzzle(
                board,
                next_node.move,
                check_ambiguity=i > 0
            )
            puzzles.append(puzzle)
        log_move(board, next_node.move, cur_score, highlight=highlight_move)
        prev_score = cur_score
        node = next_node
        i += 1
    return puzzles

