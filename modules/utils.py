import chess
import chess.uci

def sign(score):
    s = score.cp
    if s is None:
        s = score.mate
    if s > 0:
        return 1
    elif s < 0:
        return -1
    return 0

def material_total(board):
    """ Total material value on the board
    """
    return sum(v * (len(board.pieces(pt, True)) + len(board.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

def material_difference(board):
    """ Difference in material value (positive means white has more)
    """
    return sum(v * (len(board.pieces(pt, True)) - len(board.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

def material_count(board):
    """ Count the number of pieces on the board
    """
    return chess.popcount(board.occupied)

def fullmove_string(board):
    move_num = board.fullmove_number
    move_str = str(move_num)
    if board.turn:
        move_str = "%s.    " % move_str
    else:
        move_str = "%s...  " % move_str
    if move_num < 10:
        move_str += "  "
    elif move_num < 100:
        move_str += " "
    return move_str

def normalize_score(board, score):
    """ flip the signs of the score to be from white's perspective
    """
    polarity = 1 if board.turn else -1
    if score.mate is not None:
        return chess.uci.Score(None, score.mate * polarity)
    else:
        return chess.uci.Score(score.cp * polarity, None)

def should_investigate(a, b, board):
    """ determine if the difference between scores A and B
        makes the position worth investigating for a puzzle.

        A and B are normalized scores (scores from white's perspective)
    """
    if a.cp is not None and material_total(board) > 3:
        if b.cp is not None and material_count(board) > 6:
            # from an even position, the position changed by more than 1.1 cp
            if abs(a.cp) < 110 and abs(b.cp - a.cp) >= 110:
                return True
            # from a winning position, the position is now even
            elif abs(a.cp) > 200 and abs(b.cp) < 110:
                return True
            # from a winning position, a player blundered into a losing position
            elif abs(a.cp) > 200 and sign(b) != sign(a):
                return True
        elif b.mate:
            # from an even position, someone is getting checkmated
            if abs(a.cp) < 110:
                return True
            # from a major advantage, blundering and getting checkmated
            elif sign(a) != sign(b):
                return True
    elif a.mate is not None:
        if b.mate is not None:
            # blundering a checkmating position into being checkmated
            if sign(a) != sign(b):
                return True
        elif b.cp is not None:
            # blundering a mate threat into a major disadvantage
            if sign(a) != sign(b):
                return True
            # blundering a mate threat into an even position
            if abs(b.cp) < 110:
                return True
    return False
