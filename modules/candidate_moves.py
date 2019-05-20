from modules.utils import sign

def ambiguous(scores):
    """
    Looks at a list of candidate scores (best move first) to determine
    if there's a single best player move

    Returns True if a clear best move can't be determined based on these scores
    """
    if len(scores) <= 1:
        return False
    best_move_score = scores[0].cp
    second_best_move_score = scores[1].cp
    if (best_move_score is not None and second_best_move_score is not None):
        score_change = abs(second_best_move_score - best_move_score)
        if abs(best_move_score) < 50:
            # From equality, greater than 110 cp diff
            if score_change > 110:
                return False
        if best_move_score < 210:
            # Significant difference between best move and 2nd best
            if score_change > 250:
                return False
            # Slight advantage vs equality
            if abs(second_best_move_score) < 50 and score_change > 110:
                return False
            # Slight advantage vs slight disadvantage
            if sign(scores[0]) != sign(scores[1]) and score_change > 120:
                return False
            # Unclear if the best move leads to a decisive advantage
            return True
        if best_move_score < 1000:
            # If the best move is decisively better than the 2nd best move
            if best_move_score > 350 and second_best_move_score < 140:
                return False
            elif best_move_score - second_best_move_score > 500:
                return False
        if second_best_move_score > 90:
            return True
    if scores[0].mate:
        if scores[1].mate:
            if (scores[0].mate > -1 and scores[1].mate > -1):
                # More than one possible mate-in-1
                return True
        elif scores[1].cp is not None:
            if scores[1].cp > 500:
                # 2nd best move is a decisive material advantage
                return True
    return False
