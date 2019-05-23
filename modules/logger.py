import re
import logging

from chess import Move, Board
from chess.engine import Score

from modules.bcolors import bcolors
from modules.utils import fullmove_string


def log_board(board):
    """ Logs the fen string and board representation
    """
    color = bcolors.BLACK
    logging.debug(bcolors.BLUE + board.fen())
    board_str = "  " + str(board).replace("\n", "\n  ")
    board_str = re.sub("[a-z]", lambda p: bcolors.DARK_GREY + p[0] + color, board_str)
    board_str = re.sub("[A-Z]", lambda p: bcolors.WHITE + p[0] + color, board_str)
    logging.debug(color + board_str + bcolors.ENDC)

def log_move(board: Board, move: Move, score: Score,
             show_uci=False, highlight=False):
    """ 23. Qe4     CP: 123
    """
    move_str = "%s%s" % (fullmove_string(board), board.san(move))
    log_str = bcolors.GREEN
    if show_uci:
        log_str += ("  %s (%s)" % (move_str, move.uci())).ljust(22)
    else:
        log_str += "  %s" % move_str.ljust(15)
    log_str += bcolors.BLUE
    if score.is_mate():
        log_str += ("   Mate: %d" % score.mate()).ljust(12)
    else:
        log_str += ("   CP: %d" % score.score()).ljust(12)
    if highlight:
        log_str += bcolors.YELLOW + "   Investigate!"
    logging.debug(log_str + bcolors.ENDC)
