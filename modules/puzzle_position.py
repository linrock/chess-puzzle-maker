from collections import namedtuple

from modules.logger import log, log_board, log_move
from modules.colors import Color
from modules.analyzed_moves import ambiguous
from modules.analysis import AnalysisEngine, AnalyzedMove
from modules.utils import material_difference, material_count, fullmove_string


class PuzzlePosition(object):

    def __init__(self, initial_board, initial_move):
        """ board [chess.Board] - board representing the position to evaluate
            initial_move [chess.uci.Move] - the move leading into the position to evaluate
            best_move [chess.uci.Move] - the best move from the board position (after initial_move)
            score [chess.uci.Score] - the score for the board position (after initial_move)
            candidate_moves [List<AnalyzedMove>] - list of candidate moves from this position
        """
        self.initial_board = initial_board.copy()
        self.initial_move = initial_move
        self.board = initial_board.copy()
        self.board.push(initial_move)
        self.best_move = None
        self.score = None
        self.candidate_moves = []

    def _log_position(self):
        move_san = self.initial_board.san(self.initial_move)
        log(Color.BLUE, "\nAfter %s %s" % (fullmove_string(self.initial_board).strip(), move_san))
        log_board(self.board)
        log(Color.BLUE, "Material difference:  %d" % material_difference(self.board))
        log(Color.BLUE, "# legal moves:        %d" % self.board.legal_moves.count())

    def _log_move(self, move, score):
        log_move(self.board, move, score, show_uci=True)

    def _calculate_best_move(self, depth):
        """ Find the best move from board position using multipv 1
        """
        log(Color.DIM, "Evaluating best move (depth %d)..." % depth)
        best_move = AnalysisEngine.best_move(self.board, depth)
        self.best_move = best_move.move
        self.score = best_move.score
        self._log_move(self.best_move, self.score)

    def _calculate_candidate_moves(self, depth):
        """ Find the best move from board position using multipv 3
        """
        multipv = min(3, self.board.legal_moves.count())
        if multipv == 0:
            return
        log(Color.DIM, "Evaluating best %d moves (depth %d)..." % (multipv, depth))
        self.candidate_moves = AnalysisEngine.best_moves(self.board, depth, multipv)
        for analyzed_move in self.candidate_moves:
            self._log_move(analyzed_move.move, analyzed_move.score)

    def evaluate(self, depth):
        self._log_position()
        if self.board.legal_moves.count() == 0:
            return
        self._calculate_best_move(depth)
        if not self.best_move:
            return
        self._calculate_candidate_moves(depth)

    def is_ambiguous(self) -> bool:
        """ True if it's unclear whether there's a single best move from
            this position
        """
        return ambiguous([move.score for move in self.candidate_moves])

    def is_valid(self) -> bool:
        """ Is a valid puzzle position
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
