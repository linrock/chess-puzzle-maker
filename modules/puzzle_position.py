import logging
from collections import namedtuple

from modules.bcolors import bcolors
from modules.candidate_moves import ambiguous
from modules.analysis import engine
from modules.utils import material_difference, material_count, fullmove_string, normalize_score


CandidateMove = namedtuple("CandidateMove", ["move_uci", "move_san", "score"])

class PuzzlePosition(object):

    def __init__(self, initial_board, initial_move):
        """ board [chess.Board] - board representing the position to evaluate
            initial_move [chess.uci.Move] - the move leading into the position to evaluate
            best_move [chess.uci.Move] - the best move from the board position (after initial_move)
            score [chess.uci.Score] - the score for the board position (after initial_move)
            candidate_moves [List<CandidateMove>] - list of candidate moves from this position
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
        logging.debug(bcolors.BLUE + self.board.fen())
        logging.debug(bcolors.YELLOW + str(self.board) + bcolors.ENDC)
        logging.debug(bcolors.BLUE + ('Material difference:  %d' % material_difference(self.board)))
        logging.debug(bcolors.BLUE + ("# legal moves:        %d" % self.board.legal_moves.count()) + bcolors.ENDC)

    def _log_move(self, move, score):
        move_san = self.board.san(move)
        log_str = bcolors.GREEN
        log_str += ("%s%s (%s)" % (fullmove_string(self.board), move_san, move.uci())).ljust(22)
        log_str += bcolors.BLUE
        score = normalize_score(self.board, score)
        if score.mate is not None:
            log_str += "   Mate: %d" % score.mate
        else:
            log_str += "   CP: %d" % score.cp
        logging.debug(log_str + bcolors.ENDC)

    def _calculate_best_move(self, depth):
        """ Find the best move from board position using multipv 1
        """
        logging.debug(
            "%sEvaluating best move (depth %d)...%s" % (bcolors.DIM, depth, bcolors.ENDC)
        )
        engine.setoption({ "MultiPV": 1 })
        engine.position(self.board)
        self.best_move = engine.go(depth=depth).bestmove
        if self.best_move:
            self.score = engine.info_handlers[0].info["score"][1]
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
        engine.setoption({ "MultiPV": multipv })
        engine.position(self.board)
        engine.go(depth=depth)
        info = engine.info_handlers[0].info
        for i in range(multipv):
            move = info["pv"].get(i + 1)[0]
            score = info["score"].get(i + 1)
            self._log_move(move, score)
            self.candidate_moves.append(
                CandidateMove(move.uci(), self.board.san(move), score)
            )
        engine.setoption({ "MultiPV": 1 })

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
        if self.score.cp == 0 and self.board.can_claim_draw():
            return True
        if is_player_move is not None and is_player_move and self.is_ambiguous():
            return True
        return False
