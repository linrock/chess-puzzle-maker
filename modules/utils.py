import chess

def sign(a):
    if a > 0:
        return 1
    elif a < 0:
        return -1
    else:
        return 0

def material_total(board):
    return sum(v * (len(board.pieces(pt, True)) + len(board.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

def material_difference(board):
    return sum(v * (len(board.pieces(pt, True)) - len(board.pieces(pt, False))) for v, pt in zip([0,3,3,5.5,9], chess.PIECE_TYPES))

def material_count(board):
    return chess.popcount(board.occupied)

def fullmove_string(board):
    move_str = str(board.fullmove_number)
    if board.turn:
        move_str = "%s.   " % move_str
    else:
        move_str = "%s... " % move_str
    return move_str

# determine if the difference between position A and B
# is worth investigating for a puzzle.
def should_investigate(a, b, board):
    if a.cp is not None and material_total(board) > 3:
        if b.cp is not None and material_count(board) > 6:
            if a.cp > -110 and a.cp < 850 and b.cp > 200 and b.cp < 850:
                return True
            elif a.cp > -850 and a.cp < 110 and b.cp < -200 and b.cp > -850:
                return True
        elif b.mate:
            if (a.cp < 110 and sign(b.mate) == -1) or (a.cp > -110 and sign(b.mate) == 1):
                return True
    elif a.mate and b.mate:
        if sign(a.mate) == sign(b.mate): #actually means that they're opposite
            return True
    return False
