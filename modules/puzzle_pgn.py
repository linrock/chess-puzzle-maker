import chess
import chess.pgn

from modules.analysis import engine

def score_to_str(score):
    if score.mate:
        return "mate in %d" % score.mate
    else:
        return score.cp

class PuzzlePgn(object):
    """ Exports a puzzle to a PGN file
    """
    def __init__(self, puzzle):
        self.puzzle = puzzle

    def candidate_moves_annotations(self, candidate_moves):
        """ Returns the scores of the possible candidate moves
        """
        comment = ""
        for candidate_move in candidate_moves:
            comment += candidate_move.move_san
            comment += " (%s) " % score_to_str(candidate_move.score)
        return comment.strip()

    def puzzle_winner(self):
        position = self.puzzle.positions[-2]
        if position.score.mate == 1:
            return "White"
        elif position.score.mate == -1:
            return "Black"

    def export(self, pgn_headers=None) -> chess.pgn.Game:
        fen = self.puzzle.initial_board.fen()
        board = chess.Board(fen)
        game = chess.pgn.Game().from_board(board)
        game_node = game
        game_node.comment = "initial score: %s" % score_to_str(self.puzzle.initial_score)
        comment = None
        for position in self.puzzle.positions:
            game_node = game_node.add_variation(
                chess.Move.from_uci(position.initial_move.uci())
            )
            if comment:
                game_node.comment = comment
            comment = self.candidate_moves_annotations(
                position.candidate_moves
            )
        if pgn_headers:
            for h in pgn_headers:
                game.headers[h] = pgn_headers[h]
        game.headers['PuzzleEngine'] = engine.name or ""
        game.headers['PuzzleCategory'] = self.puzzle.category()
        puzzle_winner = self.puzzle_winner()
        if puzzle_winner:
            game.headers['PuzzleWinner'] = puzzle_winner
        return game
