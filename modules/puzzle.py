import logging

from modules.position_list_node import PositionListNode
from modules.puzzle_position import PuzzlePosition
from modules.puzzle_pgn import PuzzlePgn
from modules.bcolors import bcolors
from modules.analysis import engine
from modules.utils import material_difference, normalize_score

# minimum number of moves required for a puzzle to be considered complete
MIN_MOVES = 3

class Puzzle(object):
    """ last_pos [chess.Board]:
          board before the first move in the puzzle

        last_move [chess.uci.Move]:
          the first move in the puzzle

        position_list_node [PositionListNode]:
          the first position in the list of puzzle positions

        initial_score [chess.uci.Score]:
          the initial score before the first move of the puzzle

        check_ambiguity [Boolean]:
          if true, don't generate new positions when the best move is ambiguous
    """
    def __init__(self, last_pos, last_move, game, check_ambiguity=True):
        self.last_pos = last_pos.copy()
        self.last_move = last_move
        self.game = game
        self.position_list_node = PositionListNode(
            last_pos,
            last_move,
        )
        self.initial_position = PuzzlePosition(last_pos, last_move)
        self.initial_score = None
        self.final_score = None
        self.positions = []
        self.check_ambiguity = check_ambiguity

    def to_pgn(self):
        return PuzzlePgn(self).export()

    def new_to_pgn(self):
        return PuzzlePgn(self).new_export()

    def white_to_move(self):
        return self.position_list_node.position.turn

    def is_complete(self):
        if self.position_list_node.ambiguous():
            return False
        if len(self.position_list_node.move_list()) < MIN_MOVES:
            return False
        return self.position_list_node.is_complete(
            self.position_list_node.category(),
            self.white_to_move(),
            self.position_list_node.material_difference()
        )

    def generate(self, depth=22):
        self.position_list_node.generate(depth)
        if self.is_complete():
            logging.debug(bcolors.GREEN + "Puzzle is complete" + bcolors.ENDC)
        else:
            logging.debug(bcolors.RED + "Puzzle incomplete" + bcolors.ENDC)

    def category(self):
        return self.position_list_node.category()

    # TODO new methods that use the new PuzzlePosition class

    def calculate_initial_score(self, depth):
        engine.setoption({ "MultiPV": 1 })
        engine.position(self.last_pos)
        engine.go(depth=depth)
        self.initial_score = engine.info_handlers[0].info["score"][1]

    def calculate_final_score(self, depth):
        final_score = self.positions[-1].score
        if final_score:
            self.final_score = final_score
        else:
            engine.setoption({ "MultiPV": 1 })
            engine.position(self.positions[-1].board)
            engine.go(depth=depth)
            self.final_score = engine.info_handlers[0].info["score"][1]

    def new_generate(self, depth=22):
        """ Generate new positions until a final position is reached
        """
        if self.check_ambiguity:
            is_player_move = True
        else:
            logging.debug(bcolors.DIM + "Not checking this puzzle for move ambiguity")
            is_player_move = None
        self.calculate_initial_score(depth)
        position = self.initial_position
        position.evaluate()
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
                if is_player_move:
                    log_str += " one best move"
                else:
                    log_str += " not player move"
                logging.debug(log_str + bcolors.ENDC)
            position = PuzzlePosition(position.board, position.best_move, depth)
            position.evaluate()
            if self.check_ambiguity:
                is_player_move = not is_player_move
        self.calculate_final_score(depth)
        if self.new_is_complete():
            logging.debug(bcolors.GREEN + "Puzzle is complete" + bcolors.ENDC)
        else:
            logging.debug(bcolors.RED + "Puzzle incomplete" + bcolors.ENDC)

    def new_category(self):
        """ Mate     - win by checkmate
            Material - gain a material advantage
            Equalize - equalize a losing position
        """
        if self.final_score.mate is not None:
            return "Mate"
        initial_cp = self.initial_score.cp
        final_cp = self.final_score.cp
        if initial_cp is not None and final_cp is not None:
            if abs(initial_cp) > 2 and abs(final_cp) < 0.9:
                return "Equalize"
        initial_material_diff = material_difference(self.positions[0].board)
        final_material_diff = material_difference(self.positions[-1].board)
        # otherwise, the puzzle is complete only if the position was converted
        # into a material advantage
        if abs(final_material_diff - initial_material_diff) > 0.1:
            return "Material"

    def new_is_complete(self):
        """ Verify that this sequence of moves represents a complete puzzle
            Incomplete if too short or if the puzzle could not be categorized
        """
        if len(self.positions) < MIN_MOVES:
            return False
        if self.new_category():
            return True
        return False
