import re
import sys
import logging

from chess import Move, Board
from chess.engine import Score

from modules.colors import Color
from modules.utils import fullmove_string


def configure_logging(level=logging.DEBUG):
    logging.basicConfig(format="%(message)s", level=level, stream=sys.stderr)
    logging.getLogger("chess").setLevel(logging.WARNING)

def log(color: str, message: str):
    logging.debug(color + message + Color.ENDC)

def log_board(board: Board, unicode_pieces=False):
    """ Logs the fen string and board representation
    """
    color = Color.BLACK
    log(Color.VIOLET, board.fen())
    board_str = "\n  " + str(board).replace("\n", "\n  ")
    board_str = re.sub("[a-z]", lambda p: Color.DARK_GREY + p[0] + color, board_str)
    board_str = re.sub("[A-Z]", lambda p: Color.WHITE + p[0] + color, board_str)
    if unicode_pieces:
        board_str = board_str.replace("k", Color.DIM + "\u2654")
        board_str = board_str.replace("K", Color.WHITE + "\u2654")
        board_str = board_str.replace("q", Color.DIM + "\u2655")
        board_str = board_str.replace("Q", Color.WHITE + "\u2655")
        board_str = board_str.replace("r", Color.DIM + "\u2656")
        board_str = board_str.replace("R", Color.WHITE + "\u2656")
        board_str = board_str.replace("b", Color.DIM + "\u2657")
        board_str = board_str.replace("B", Color.WHITE + "\u2657")
        board_str = board_str.replace("n", Color.DIM + "\u2658")
        board_str = board_str.replace("N", Color.WHITE + "\u2658")
        board_str = board_str.replace("p", Color.DIM + "\u2659")
        board_str = board_str.replace("P", Color.WHITE + "\u2659")
    log(color, board_str + "\n")

def log_move(board: Board, move: Move, score: Score,
             show_uci=False, highlight=False):
    """ 23. Qe4     CP: 123
    """
    move_str = "%s%s" % (fullmove_string(board), board.san(move))
    if show_uci:
        log_str = ("  %s (%s)" % (move_str, move.uci())).ljust(22)
    else:
        log_str = "  %s" % move_str.ljust(15)
    log_str += Color.BLUE
    if score.is_mate():
        log_str += ("   Mate: %d" % score.mate()).ljust(12)
    else:
        log_str += ("   CP: %d" % score.score()).ljust(12)
    if highlight:
        log_str += Color.YELLOW + "   Investigate!"
    log(Color.GREEN, log_str)
