def ambiguous(moves):
    """
    Looks at a list of candidate moves (sorted by score) to determine
    if there's a single best player move

    Returns True if a clear best move can't be determined
    """
    if len(moves) <= 1:
        return False
    # If strict == False then it will generate more tactics but more ambiguous
    # move_number = 1 if self.strict == True else 2
    best_move_score = moves[0].evaluation.cp
    second_best_move_score = moves[1].evaluation.cp
    if (best_move_score is not None and second_best_move_score is not None):
        if best_move_score < 210:
            # Unclear if the best move leads to a decisive advantage
            return True
        if best_move_score < 1000:
            # If the best move is decisively better than the 2nd best move
            if best_move_score > 500 and second_best_move_score < 140:
                return False
            elif best_move_score - second_best_move_score > 500:
                return False
        if second_best_move_score > 90:
            return True
    if moves[0].evaluation.mate:
        if moves[1].evaluation.mate:
            if (moves[0].evaluation.mate > -1 and moves[1].evaluation.mate > -1):
                # More than one possible mate-in-1
                return True
        elif moves[1].evaluation.cp is not None:
            if moves[1].evaluation.cp > 500:
                # 2nd best move is a decisive material advantage
                return True
    return False
