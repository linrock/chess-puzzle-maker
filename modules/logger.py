import re
import logging

from chess import Move, Board
from chess.engine import Score

from modules.colors import Color
from modules.utils import fullmove_string


def log(message: str):
    logging.debug(message + Color.ENDC)

def log_board(board: Board):
    """ Logs the fen string and board representation
    """
    color = Color.BLACK
    log(Color.BLUE + board.fen())
    board_str = "  " + str(board).replace("\n", "\n  ")
    board_str = re.sub("[a-z]", lambda p: Color.DARK_GREY + p[0] + color, board_str)
    board_str = re.sub("[A-Z]", lambda p: Color.WHITE + p[0] + color, board_str)
    log(color + board_str)

def log_move(board: Board, move: Move, score: Score,
             show_uci=False, highlight=False):
    """ 23. Qe4     CP: 123
    """
    move_str = "%s%s" % (fullmove_string(board), board.san(move))
    log_str = Color.GREEN
    if show_uci:
        log_str += ("  %s (%s)" % (move_str, move.uci())).ljust(22)
    else:
        log_str += "  %s" % move_str.ljust(15)
    log_str += Color.BLUE
    if score.is_mate():
        log_str += ("   Mate: %d" % score.mate()).ljust(12)
    else:
        log_str += ("   CP: %d" % score.score()).ljust(12)
    if highlight:
        log_str += Color.YELLOW + "   Investigate!"
    log(log_str)
