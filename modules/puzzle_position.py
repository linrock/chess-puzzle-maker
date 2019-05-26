from typing import List
from collections import namedtuple

from chess import Board, Move
from chess.engine import Score

from modules.logger import log, log_board, log_move
from modules.colors import Color
from modules.analysis import AnalysisEngine, AnalyzedMove, ambiguous_best_move
from modules.utils import material_difference, material_count, fullmove_string
from modules.constants import NUM_CANDIDATE_MOVES


class PuzzlePosition(object):

    def __init__(self, initial_board: Board, initial_move: Move):
        """ board [Board] - board representing the position to evaluate
            initial_move [Move] - the move leading into the position to evaluate
            best_move [Move] - the best move from the board position (after initial_move)
            score [Score] - the score for the board position (after initial_move)
            candidate_moves [List<AnalyzedMove>] - best candidate moves from this position
        """
        self.initial_board: Board = initial_board.copy()
        self.initial_move: Move = initial_move
        self.board = initial_board.copy()
        if initial_move:
            self.board.push(initial_move)
        self.best_move: Move = None
        self.score: Score = None
        self.candidate_moves: List[AnalyzedMove] = []

    def _log_position(self):
        move_san = self.initial_board.san(self.initial_move)
        log(Color.VIOLET, "\nAfter %s %s" % (fullmove_string(self.initial_board).strip(), move_san))
        log_board(self.board)
        log(Color.DARK_BLUE, "Material difference:  %d" % material_difference(self.board))
        log(Color.DARK_BLUE, "# legal moves:        %d" % self._num_legal_moves())

    def _log_move(self, move, score):
        log_move(self.board, move, score, show_uci=True)

    def _num_legal_moves(self) -> int:
        return self.board.legal_moves.count()

    def _calculate_best_move(self, depth):
        """ Find the best move from board position using multipv 1
        """
        log(Color.BLACK, "Evaluating best move (depth %d)..." % depth)
        best_move = AnalysisEngine.best_move(self.board, depth)
        self.best_move = best_move.move
        self.score = best_move.score
        if self._num_legal_moves() == 1:
            self.candidate_moves = [best_move]
        self._log_move(self.best_move, self.score)

    def _calculate_candidate_moves(self, depth):
        """ Find the best move from board position using multipv 3
        """
        multipv = NUM_CANDIDATE_MOVES
        log(Color.BLACK, "Evaluating best %d moves (depth %d)..." % (multipv, depth))
        self.candidate_moves = AnalysisEngine.best_moves(self.board, depth, multipv)
        for analyzed_move in self.candidate_moves:
            self._log_move(analyzed_move.move, analyzed_move.score)

    def evaluate(self, depth):
        self._log_position()
        if self._num_legal_moves() == 0:
            return
        self._calculate_best_move(depth)
        if not self.best_move:
            return
        if self._num_legal_moves() > 1:
            self._calculate_candidate_moves(depth)

    def is_mate(self) -> bool:
        return self.score and self.score.is_mate()

    def is_ambiguous(self) -> bool:
        """ True if it's unclear whether there's a single best move from
            this position
        """
        return ambiguous_best_move([move.score for move in self.candidate_moves])

    def is_valid(self) -> bool:
        """ Is a valid position for generating a follow-up position
        """
        if not self.best_move or len(self.candidate_moves) == 0:
            return False
        return not self.is_ambiguous() and not self.board.is_game_over()

    def is_final(self, is_player_move=None) -> bool:
        """ No more positions can exist after this position in a puzzle
            either because the position is ambiguous or because the game is over
        """
        if not self.best_move or len(self.candidate_moves) == 0:
            return True
        if self.board.is_game_over():
            return True
        if self.score.score() == 0 and self.board.can_claim_draw():
            return True
        if is_player_move is not None and is_player_move and self.is_ambiguous():
            return True
        return False
