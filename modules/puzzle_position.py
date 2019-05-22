import logging
from collections import namedtuple

from chess.engine import Limit

from modules.logger import log_board, log_move
from modules.bcolors import bcolors
from modules.analyzed_moves import AnalyzedMove, ambiguous
from modules.analysis import AnalysisEngine 
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
        logging.debug(bcolors.BLUE + ("After %s %s" % (fullmove_string(self.initial_board).strip(), move_san)))
        log_board(self.board)
        logging.debug(bcolors.BLUE + ('Material difference:  %d' % material_difference(self.board)))
        logging.debug(bcolors.BLUE + ("# legal moves:        %d" % self.board.legal_moves.count()) + bcolors.ENDC)

    def _log_move(self, move, score):
        log_move(self.board, move, score, show_uci=True)

    def _calculate_best_move(self, depth):
        """ Find the best move from board position using multipv 1
        """
        logging.debug(
            "%sEvaluating best move (depth %d)...%s" % (bcolors.DIM, depth, bcolors.ENDC)
        )
        info = AnalysisEngine.instance().analyse(self.board, Limit(depth=depth))
        pv = info["pv"]
        if len(pv) > 0:
            self.best_move = pv[0]
        if self.best_move:
            self.score = info["score"].white()
            self._log_move(self.best_move, self.score)
        else:
            logging.debug(bcolors.RED + "No best move!" + bcolors.ENDC)

    def _calculate_candidate_moves(self, depth):
        """ Find the best move from board position using multipv 3
        """
        multipv = min(3, self.board.legal_moves.count())
        if multipv == 0:
            return
        logging.debug(bcolors.DIM + ("Evaluating best %d moves (depth %d)..." % (multipv, depth)) + bcolors.ENDC)
        multipv_info = AnalysisEngine.instance().analyse(self.board, Limit(depth=depth), multipv=multipv)
        for info in multipv_info:
            move = info["pv"][0]
            score = info["score"].white()
            self._log_move(move, score)
            self.candidate_moves.append(
                AnalyzedMove(move.uci(), self.board.san(move), score)
            )

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
