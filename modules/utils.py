import chess
from chess.engine import Score

def sign(score) -> int:
    if score.is_mate():
        s = score.mate()
    else:
        s = score.score()
    if s > 0:
        return 1
    elif s < 0:
        return -1
    return 0

def material_total(board) -> float:
    """ Total material value on the board
    """
    return sum(v * (len(board.pieces(pt, True)) + len(board.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

def material_difference(board) -> float:
    """ Difference in material value (positive means white has more)
    """
    return sum(v * (len(board.pieces(pt, True)) - len(board.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

def material_count(board) -> int:
    """ Count the number of pieces on the board
    """
    return chess.popcount(board.occupied)

def fullmove_string(board) -> str:
    move_num = board.fullmove_number
    if board.turn:
        move_str = "%s." % move_num
    else:
        move_str = "%s..." % move_num
    return move_str.ljust(7)

def should_investigate(a: Score, b: Score, board: chess.Board) -> bool:
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
        elif b.mate:
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
