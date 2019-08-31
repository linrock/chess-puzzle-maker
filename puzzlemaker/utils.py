from chess import PIECE_TYPES, Board, popcount
from chess.engine import Score


def sign(score: Score) -> int:
    if score.is_mate():
        s = score.mate()
    else:
        s = score.score()
    if s > 0:
        return 1
    elif s < 0:
        return -1
    return 0

def material_total(board: Board) -> float:
    """ Total material value on the board
    """
    value = 0
    for v, pt in zip([0,3,3,5.5,9], PIECE_TYPES):
        value += v * (len(board.pieces(pt, True)) + len(board.pieces(pt, False)))
    return value

def material_difference(board: Board) -> float:
    """ Difference in material value (positive means white has more)
    """
    diff = 0
    for v, pt in zip([0,3,3,5.5,9], PIECE_TYPES):
        diff += v * (len(board.pieces(pt, True)) - len(board.pieces(pt, False)))
    return diff

def material_count(board: Board) -> int:
    """ Count the number of pieces on the board
    """
    return popcount(board.occupied)

def fullmove_string(board: Board) -> str:
    """ 1. e4
        2... d5
    """
    move_num = board.fullmove_number
    if board.turn:
        move_str = "%s." % move_num
    else:
        move_str = "%s..." % move_num
    return move_str.ljust(7)
