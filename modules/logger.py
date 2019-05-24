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

def log_board(board: Board, unicode_pieces=True):
    """ Logs the fen string and board representation
    """
    log(Color.VIOLET, board.fen())
    sq_color = Color.BLACK
    white_color = Color.WHITE
    black_color = Color.DARK_GREY
    board_str = "\n  " + str(board).replace("\n", "\n  ")
    board_str = re.sub("[a-z]", lambda p: white_color + p[0] + sq_color, board_str)
    board_str = re.sub("[A-Z]", lambda p: black_color + p[0] + sq_color, board_str)
    if unicode_pieces:
        piece_map = {
            "k": "\u2654",
            "q": "\u2655",
            "r": "\u2656",
            "b": "\u2657",
            "n": "\u2658",
            "p": "\u2659",
        }
        for p, code in piece_map.items():
            board_str = board_str.replace(p, code).replace(p.capitalize(), code)
    log(sq_color, board_str + "\n")

def log_move(board: Board, move: Move, score: Score,
             show_uci=False, highlight=False):
    """ 23. Qe4     CP: 123
    """
    move_str = "%s%s" % (fullmove_string(board), board.san(move))
    log_str = "  %s" % move_str
    if show_uci:
        log_str += "%s (%s)" % (Color.DARK_GREEN, move.uci())
        log_str = log_str.ljust(22 + len(Color.DARK_GREEN))
    else:
        log_str = log_str.ljust(15)
    log_str += Color.ENDC + Color.BLUE
    if score.is_mate():
        log_str += ("   Mate: %d" % score.mate()).ljust(12)
    else:
        log_str += ("   CP: %d" % score.score()).ljust(12)
    if highlight:
        log_str += Color.YELLOW + "   Investigate!"
    log(Color.GREEN, log_str)
