import logging

from modules.position_list_node import PositionListNode
from modules.puzzle_pgn import PuzzlePgn
from modules.bcolors import bcolors

# minimum number of moves required for a puzzle to be considered complete
MIN_MOVES = 3

class Puzzle(object):
    """ last_pos = chess.Board instance
    """
    def __init__(self, last_pos, last_move, game, strict):
        self.last_pos = last_pos.copy()
        self.last_move = last_move
        self.game = game
        self.position_list_node = PositionListNode(
            last_pos,
            last_move,
            strict=strict
        )

    def to_pgn(self):
        return PuzzlePgn(self).export()

    def color(self):
        return self.position_list_node.position.turn

    def is_complete(self):
        if self.position_list_node.ambiguous():
            return False
        if len(self.position_list_node.move_list()) < MIN_MOVES:
            return False
        return self.position_list_node.is_complete(
            self.position_list_node.category(),
            self.color(),
            True,
            self.position_list_node.material_difference()
        )

    def generate(self, depth=22):
        self.position_list_node.generate(depth)
        if self.is_complete():
            logging.debug(bcolors.GREEN + "Puzzle is complete" + bcolors.ENDC)
        else:
            logging.debug(bcolors.FAIL + "Puzzle incomplete" + bcolors.ENDC)

    def category(self):
        return self.position_list_node.category()
