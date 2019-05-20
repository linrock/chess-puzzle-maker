import chess
import chess.pgn

from modules.analysis import engine

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
            if candidate_move.evaluation.mate:
                comment += " (mate in %d) " % candidate_move.evaluation.mate
            else:
                comment += " (%d) " % candidate_move.evaluation.cp
        return comment.strip()

    def new_candidate_moves_annotations(self, candidate_moves):
        """ Returns the scores of the possible candidate moves
        """
        comment = ""
        for candidate_move in candidate_moves:
            comment += candidate_move.move_san
            if candidate_move.score.mate:
                comment += " (mate in %d) " % candidate_move.score.mate
            else:
                comment += " (%d) " % candidate_move.score.cp
        return comment.strip()

    def puzzle_winner(self):
      node = self.puzzle.position_list_node
      while node.next_position and node.next_position.evaluation:
          node = node.next_position
      score = node.evaluation
      if score.mate == 1:
          return "White"
      elif score.mate == -1:
          return "Black"

    def export(self):
        """ Returns a chess.Game instance
        """
        puzzle = self.puzzle
        fen = puzzle.last_pos.fen()
        board = chess.Board(fen)
        game = chess.pgn.Game().from_board(board)
        game_node = game.add_variation(puzzle.last_move)
        position_list_node = puzzle.position_list_node
        for m in position_list_node.move_list():
            game_node = game_node.add_variation(chess.Move.from_uci(m))
            game_node.comment = self.candidate_moves_annotations(
                position_list_node.candidate_moves
            )
            position_list_node = position_list_node.next_position
        for h in puzzle.game.headers:
            game.headers[h] = puzzle.game.headers[h]
        game.headers['PuzzleEngine'] = engine.name or ""
        puzzle_winner = self.puzzle_winner()
        if puzzle_winner:
            game.headers['PuzzleWinner'] = puzzle_winner
        return game

    def new_export(self):
        fen = self.puzzle.last_pos.fen()
        board = chess.Board(fen)
        game = chess.pgn.Game().from_board(board)
        game_node = game
        comment = None
        for position in self.puzzle.positions:
            game_node = game_node.add_variation(
                chess.Move.from_uci(position.initial_move.uci())
            )
            if comment:
                game_node.comment = comment
            comment = self.new_candidate_moves_annotations(
                position.candidate_moves
            )
        if self.puzzle.game:
            for h in self.puzzle.game.headers:
                game.headers[h] = self.puzzle.game.headers[h]
        game.headers['PuzzleEngine'] = engine.name or ""
        game.headers['PuzzleCategory'] = self.puzzle.new_category()
        puzzle_winner = self.puzzle_winner()
        if puzzle_winner:
            game.headers['PuzzleWinner'] = puzzle_winner
        return game
