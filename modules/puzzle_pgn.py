import chess
import chess.pgn

class PuzzlePgn(object):
    """ Exports a puzzle to a PGN file
    """
    def __init__(self, puzzle):
        self.puzzle = puzzle

    def candidate_moves_annotations(self, candidate_moves):
        """ Returns the scores of the possible candidate moves
        """
        comment = ""
        for analysis in candidate_moves:
            comment += analysis.move_san
            if analysis.evaluation.mate:
                comment += " (mate in %d) " % analysis.evaluation.mate
            else:
                comment += " (%d) " % analysis.evaluation.cp
        return comment.strip()

    def export(self):
        """ Returns a chess.Game instance
        """
        puzzle = self.puzzle
        fen = puzzle.last_pos.fen()
        board = chess.Board(fen)
        game = chess.pgn.Game().from_board(board)
        
        # In the tactic the first to move is the one who lost
        result = '1-0' # result of the tactic not the game
        if board.turn: # turn return true if white
            result = '0-1'

        node = game.add_variation(puzzle.last_move)
        position_list_node = puzzle.position_list_node
        for m in position_list_node.move_list():
            node = node.add_variation(chess.Move.from_uci(m))
            node.comment = self.candidate_moves_annotations(
                position_list_node.candidate_moves
            )
            position_list_node = position_list_node.next_position
        for h in puzzle.game.headers:
            game.headers[h] = puzzle.game.headers[h]
        game.headers['PuzzleEngine'] = puzzle.engine.name
        game.headers['PuzzleResult'] = result
        return game
