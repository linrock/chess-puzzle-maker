import logging
from typing import List

from chess import Board
from chess.pgn import Game
from chess.engine import Score, Cp, Limit

from modules.logger import log_move
from modules.bcolors import bcolors
from modules.analysis import AnalysisEngine
from modules.puzzle import Puzzle
from modules.utils import sign, material_total, material_count


def find_puzzle_candidates(game: Game, scan_depth=16) -> List[Puzzle]:
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
        info = AnalysisEngine.instance().analyse(next_board, Limit(depth=scan_depth))
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
                # check_ambiguity=True,
                # check_ambiguity=i > 0
            )
            puzzles.append(puzzle)
        log_move(board, next_node.move, cur_score, highlight=highlight_move)
        prev_score = cur_score
        node = next_node
        i += 1
    return puzzles

def should_investigate(a: Score, b: Score, board: Board) -> bool:
    """ determine if the difference between scores A and B
        makes the position worth investigating for a puzzle.

        A and B are normalized scores (scores from white's perspective)
    """
    a_cp = a.score()
    b_cp = b.score()
    if a_cp is not None and material_total(board) > 3:
        if b_cp is not None and material_count(board) > 6:
            # from an even position, the position changed by more than 1.1 cp
            if abs(a_cp) < 110 and abs(b_cp - a_cp) >= 110:
                return True
            # from a winning position, the position is now even
            elif abs(a_cp) > 200 and abs(b_cp) < 110:
                return True
            # from a winning position, a player blundered into a losing position
            elif abs(a_cp) > 200 and sign(b) != sign(a):
                return True
        elif b.is_mate():
            # from an even position, someone is getting checkmated
            if abs(a_cp) < 110:
                return True
            # from a major advantage, blundering and getting checkmated
            elif sign(a) != sign(b):
                return True
    elif a.is_mate():
        if b.is_mate():
            # blundering a checkmating position into being checkmated
            if b.mate() != 0 and sign(a) != sign(b):
                return True
        elif b_cp is not None:
            # blundering a mate threat into a major disadvantage
            if sign(a) != sign(b):
                return True
            # blundering a mate threat into an even position
            if abs(b_cp) < 110:
                return True
    return False
