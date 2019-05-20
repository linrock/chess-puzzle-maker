import logging
from collections import namedtuple

from modules.bcolors import bcolors
from modules.candidate_moves import ambiguous
from modules.analysis import engine


CandidateMove = namedtuple("CandidateMove", ["move_uci", "move_san", "score"])

# The search depth used to calculate the best move and 
# candidate moves for the board position
SEARCH_DEPTH = 22

class PuzzlePosition(object):

    def __init__(self, initial_board, initial_move, search_depth=SEARCH_DEPTH):
        """ board [chess.Board] - board representing the position to evaluate
            initial_move [chess.uci.Move] - the move leading into the position to evaluate
            best_move [chess.uci.Move] - the best move from the board position
            score [chess.uci.Score] - score for the current position
            candidate_moves [List<CandidateMove>] - list of candidate moves from this position
        """
        self.initial_board = initial_board.copy()
        self.initial_move = initial_move
        self.board = initial_board.copy()
        self.board.push(initial_move)
        self.best_move = None
        self.score = None
        self.candidate_moves = []
        self.search_depth = search_depth

    def evaluate(self):
        if self.board.legal_moves.count() == 0:
            return
        self.calculate_best_move()           
        if not self.best_move:
            return
        self.calculate_candidate_moves()

    def calculate_best_move(self):
        """ Find the best move from board position using multipv 1
        """
        engine.setoption({ "MultiPV": 1 })
        engine.position(self.board)
        self.best_move = engine.go(depth=self.search_depth).bestmove
        if self.best_move:
            self.score = engine.info_handlers[0].info["score"][1]
        # self._log_move(self.best_move, self.score)

    def calculate_candidate_moves(self):
        """ Find the best move from board position using multipv 3
        """
        multipv = min(3, self.board.legal_moves.count())
        engine.setoption({ "MultiPV": multipv })
        engine.position(self.board)
        engine.go(depth=self.search_depth)
        info = engine.info_handlers[0].info
        for i in range(multipv):
            move = info["pv"].get(i + 1)[0]
            score = info["score"].get(i + 1)
            # print(move, score)
            # self._log_move(move, score)
            self.candidate_moves.append(
                CandidateMove(move.uci(), self.board.san(move), score)
            )
        engine.setoption({ "MultiPV": 1 })

    def is_ambiguous(self):
        """ True if it's unclear whether there's a single best move from
            this position
        """
        return ambiguous([move.score for move in self.candidate_moves])

    def is_valid(self):
        """ Is a valid puzzle position
        """
        if not self.best_move or len(self.candidate_moves) == 0:
            return False
        return not self.is_ambiguous() and not self.board.is_game_over()

    def is_final(self):
        """ No more positions can exist after this position in a puzzle
            either because the position is ambiguous or because the game is over
        """
        if not self.best_move or len(self.candidate_moves) == 0:
            return True
        if self.is_ambiguous() or self.board.is_game_over():
            return True
        if self.score.cp == 0 and self.board.can_claim_draw():
            return True
        return False

