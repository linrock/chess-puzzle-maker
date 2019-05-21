import logging

import chess.engine
import chess.pgn

from modules.puzzle_position import PuzzlePosition
from modules.puzzle_pgn import PuzzlePgn
from modules.bcolors import bcolors
from modules.analysis import engine
from modules.utils import material_difference

# minimum number of moves required for a puzzle to be considered complete
MIN_MOVES = 3

class Puzzle(object):
    """ initial_board [chess.Board]:
          the board before the first move in the puzzle

        initial_move [chess.uci.Move]:
          the first move in the puzzle

        initial_score [chess.uci.Score]:
          the initial score before the first move of the puzzle

        positions [list(PuzzlePosition)]:
          list of all positions included in the puzzle

        check_ambiguity [Boolean]:
          if true, don't generate new positions when the best move is ambiguous
    """
    def __init__(self, initial_board, initial_move, check_ambiguity=True):
        self.initial_board = initial_board.copy()
        self.initial_move = initial_move
        self.initial_position = PuzzlePosition(initial_board, initial_move)
        self.initial_score = None
        self.final_score = None
        self.positions = []
        # self.check_ambiguity = check_ambiguity
        self.check_ambiguity = True

    def _calculate_initial_score(self, depth):
        """ multipv 1 """
        # engine.setoption({ "MultiPV": 1 })
        info = engine.analyse(self.initial_board, chess.engine.Limit(depth=depth))
        self.initial_score = info["score"].white()

    def _calculate_final_score(self, depth):
        """ multipv 1 """
        final_score = self.positions[-1].score
        if final_score:
            self.final_score = final_score
        else:
            # engine.setoption({ "MultiPV": 1 })
            info = engine.analyse(self.positions[-1].board, chess.engine.Limit(depth=depth))
            self.final_score = info["score"].white()

    def export(self, pgn_headers=None) -> chess.pgn.Game:
        return PuzzlePgn(self).export(pgn_headers)

    def generate(self, depth):
        """ Generate new positions until a final position is reached
        """
        if self.check_ambiguity:
            is_player_move = True
        else:
            logging.debug(bcolors.DIM + "Not checking for move ambiguity" + bcolors.ENDC)
            is_player_move = None
        self._calculate_initial_score(depth)
        position = self.initial_position
        position.evaluate(depth)
        while True:
            self.positions.append(position)
            if position.is_final(is_player_move):
                log_str = "Not going deeper: "
                if position.is_ambiguous():
                    log_str += "ambiguous"
                elif position.board.is_game_over():
                    log_str += "game over"
                logging.debug(bcolors.YELLOW + log_str + bcolors.ENDC)
                break
            else:
                log_str = bcolors.DIM + "Going deeper..."
                if is_player_move is not None:
                    if is_player_move:
                        log_str += " one best move"
                    else:
                        log_str += " not player move"
                logging.debug(log_str + bcolors.ENDC)
            position = PuzzlePosition(position.board, position.best_move)
            position.evaluate(depth)
            if self.check_ambiguity:
                is_player_move = not is_player_move
        self._calculate_final_score(depth)
        if self.is_complete():
            logging.debug(bcolors.GREEN + "Puzzle is complete" + bcolors.ENDC)
        else:
            logging.debug(bcolors.RED + "Puzzle incomplete" + bcolors.ENDC)

    def category(self) -> str:
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
            # otherwise, the puzzle is complete only if the evaluation changed from
            # the initial position and was converted into a material advantage
            if abs(final_cp - initial_cp) > 100:
                initial_material_diff = material_difference(self.positions[0].board)
                final_material_diff = material_difference(self.positions[-1].board)
                if abs(final_material_diff - initial_material_diff) > 0.1:
                    return "Material"

    def winner(self) -> str:
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

    def is_complete(self) -> bool:
        """ Verify that this sequence of moves represents a complete puzzle
            Incomplete if too short or if the puzzle could not be categorized
        """
        if len(self.positions) < MIN_MOVES:
            return False
        if self.category():
            return True
        return False
