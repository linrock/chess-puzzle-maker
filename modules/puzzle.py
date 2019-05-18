import logging

from modules.position_list_node import PositionListNode
from modules.puzzle_pgn import PuzzlePgn
from modules.bcolors import bcolors

# minimum number of movies required for a puzzle to be considered complete
MIN_MOVES = 2

class Puzzle(object):
    """ last_pos = chess.Board instance
    """
    def __init__(self, last_pos, last_move, game_id, engine, info_handler, game, strict):
        self.last_pos = last_pos.copy()
        self.last_move = last_move
        self.game_id = game_id
        self.engine = engine
        last_pos.push(last_move)
        self.position_list_node = PositionListNode(
            last_pos, engine, info_handler, strict
        )
        self.game = game

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'category': self.position_list_node.category(),
            'last_pos': self.last_pos.fen(),
            'last_move': self.last_move.uci(),
            'move_list': self.position_list_node.move_list()
        }

    def to_pgn(self):
        return PuzzlePgn(self).export()

    def color(self):
        return self.position_list_node.position.turn

    def is_complete(self):
        return (
            self.position_list_node.is_complete(
                self.position_list_node.category(),
                self.color(), 
                True, 
                self.position_list_node.material_difference()
            )
            and not self.position_list_node.ambiguous()
            and len(self.position_list_node.move_list()) > MIN_MOVES
        )

    def generate(self, depth):
        self.position_list_node.generate(depth)
        if self.is_complete():
            logging.debug(bcolors.OKGREEN + "Puzzle is complete" + bcolors.ENDC)
        else:
            logging.debug(bcolors.FAIL + "Puzzle incomplete" + bcolors.ENDC)

    def category(self):
        return self.position_list_node.category()
