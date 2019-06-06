from collections import namedtuple
from typing import Optional

from chess import Move
import chess.pgn

from modules.puzzle_position import PuzzlePosition
from modules.puzzle_exporter import PuzzleExporter
from modules.logger import log, log_board, log_move
from modules.colors import Color
from modules.analysis import AnalysisEngine, AnalyzedMove
from modules.utils import material_difference
from modules.constants import MIN_PLAYER_MOVES


class Puzzle(object):
    """ initial_board [chess.Board]:
          the board before the first move in the puzzle

        initial_move [chess.uci.Move]:
          the first move in the puzzle

        initial_score [chess.uci.Score]:
          the initial score before the first move of the puzzle

        initial_position [PuzzlePosition]:
          the first position of the puzzle
          uses the initial move if there is one
          otherwise, uses the best analyzed move

        positions [list(PuzzlePosition)]:
          list of all positions included in the puzzle

        analyzed_moves [list(AnalyzedMove)]:
          list of analyzed possible first moves

        check_ambiguity [Boolean]:
          if true, don't generate new positions when the best move is ambiguous
    """
    def __init__(self, initial_board, initial_move=None):
        self.initial_score = None
        self.initial_board = initial_board.copy()
        self.initial_move = initial_move
        self.initial_position = None
        self.final_score = None
        self.positions = []
        self.analyzed_moves = []

    def _analyze_best_initial_move(self, depth) -> Move:
        log(Color.BLACK, "Evaluating best initial move (depth %d)..." % depth)
        best_move = AnalysisEngine.best_move(self.initial_board, depth)
        if best_move.move:
            self.analyzed_moves.append(best_move)
            log_move(self.initial_board, best_move.move, best_move.score, show_uci=True)
        self.initial_score = best_move.score
        return best_move.move

    def _analyze_initial_moves(self, depth):
        """ get the score of the position before the initial move
            also get the score of the position after the initial move
        """
        best_move = self._analyze_best_initial_move(depth)
        if not self.initial_move:
            return
        elif self.initial_move == best_move:
            log(Color.BLACK, "The move played was the best move")
        else:
            log(Color.BLACK, "Evaluating played initial move (depth %d)..." % depth)
            analyzed_move = AnalysisEngine.evaluate_move(self.initial_board, self.initial_move, depth)
            self.analyzed_moves.append(analyzed_move)
            log_move(self.initial_board, self.initial_move, analyzed_move.score, show_uci=True)

    def _set_initial_position(self):
        initial_move = self.initial_move
        if not initial_move and len(self.analyzed_moves) > 0:
            initial_move = self.analyzed_moves[0].move
        self.initial_position = PuzzlePosition(self.initial_board, initial_move)

    def _player_moves_first(self) -> bool:
        """ Determines if the player makes the first move in this puzzle
            If yes, the first move is the best move (i.e. winning position, checkmate puzzle)
            If no, the first move is a blunder/mistake by the opponent
        """
        if self.initial_score.is_mate() and not self.initial_move:
            # it's a checkmate puzzle without a move sequence
            white_to_move = self.initial_board.turn
            if white_to_move and self.initial_score.mate() > 0:
                return True
            elif not white_to_move and self.initial_score.mate() < 0:
                return True
        elif self.initial_move and self.initial_position.is_mate():
            # player just moved and has a winning position to checkmate the opponent
            white_just_moved = not self.initial_position.board.turn
            if self.initial_score.is_mate():
                if white_just_moved and self.initial_score.mate() > 0:
                    return True
                elif not white_just_moved and self.initial_score.mate() < 0:
                    return True
        # assume the initial move is a blunder/mistake by the opponent
        if self.initial_move:
            return False
        else:
            return True

    def _calculate_final_score(self, depth):
        """ Get the score of the final board position in the puzzle
            after the last move is made
        """
        final_score = self.positions[-1].score
        if final_score:
            self.final_score = final_score
        else:
            self.final_score = AnalysisEngine.score(self.positions[-1].board, depth)

    def generate(self, depth):
        """ Generate new positions for the puzzle until a final position is reached
        """
        log_board(self.initial_board)
        self._analyze_initial_moves(depth)
        self._set_initial_position()
        position = self.initial_position
        position.evaluate(depth)
        self.player_moves_first = self._player_moves_first()
        is_player_move = not self.player_moves_first
        while True:
            self.positions.append(position)
            if position.is_final(is_player_move):
                log_str = "Not going deeper: "
                if position.is_ambiguous():
                    log_str += "ambiguous"
                elif position.board.is_game_over():
                    log_str += "game over"
                log(Color.YELLOW, log_str)
                break
            else:
                log_str = "Going deeper..."
                if is_player_move is not None:
                    if is_player_move:
                        if len(position.candidate_moves) == 1:
                            log_str += " only one move"
                        else:
                            log_str += " one clear best move"
                    else:
                        log_str += " not player move"
                log(Color.DIM, log_str)
            position = PuzzlePosition(position.board, position.best_move)
            position.evaluate(depth)
            is_player_move = not is_player_move
        self._calculate_final_score(depth)
        if self.is_complete():
            log(Color.GREEN, "Puzzle is complete")
        else:
            log(Color.RED, "Puzzle incomplete")

    def to_pgn(self, pgn_headers=None) -> chess.pgn.Game:
        return PuzzleExporter(self).to_pgn(pgn_headers)

    def category(self) -> Optional[str]:
        """ Mate     - win by checkmate
            Material - gain a material advantage
            Equalize - equalize a losing position
        """
        if self.final_score.is_mate():
            return "Mate"
        initial_cp = self.initial_score.score()
        final_cp = self.final_score.score()
        if initial_cp is not None and final_cp is not None:
            # going from a disadvantage to an equal position
            if abs(initial_cp) > 2 and abs(final_cp) < 0.9:
                return "Equalize"
            # otherwise, the puzzle is only complete if the score changed
            # significantly after the initial position and was converted
            # into a material advantage
            initial_material_diff = material_difference(self.positions[0].initial_board)
            final_material_diff = material_difference(self.positions[-1].board)
            if abs(final_material_diff - initial_material_diff) > 0.1:
                if abs(final_cp - initial_cp) > 100:
                    return "Material"
                elif not self.initial_move:
                    # a puzzle from a position, not a sequence of moves
                    if final_cp > 100 or final_cp < -100:
                        return "Material"

    def winner(self) -> Optional[str]:
        """ Find the winner of the puzzle based on the move sequence
        """
        position = self.positions[-2]
        if position.score.mate() == 1:
            return "White"
        elif position.score.mate() == -1:
            return "Black"
        initial_cp = self.initial_score.score()
        final_cp = self.final_score.score()
        if initial_cp is not None and final_cp is not None:
            # evaluation change favors white
            if final_cp - initial_cp > 100:
                return "White"
            # evaluation change favors black
            elif final_cp - initial_cp < -100:
                return "Black"
            # evaluation equalized after initially favoring black
            elif initial_cp < 0 and abs(final_cp) < 50:
                return "White"
            # evaluation equalized after initially favoring white
            elif initial_cp > 0 and abs(final_cp) < 50:
                return "Black"
        if not self.initial_move and final_cp:
            # a puzzle from a position, not a sequence of moves
            if final_cp > 100:
                return "White"
            elif final_cp < -100:
                return "Black"

    def is_complete(self) -> bool:
        """ Verify that this sequence of moves represents a complete puzzle
            Incomplete if too short or if the puzzle could not be categorized
        """
        n_player_moves = 1 if self.player_moves_first else 0
        n_player_moves += int((len(self.positions) - 1) / 2)
        if n_player_moves < MIN_PLAYER_MOVES:
            return False
        if self.category():
            return True
        return False
