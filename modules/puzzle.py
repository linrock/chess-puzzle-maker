import os
import json
import logging

import chess
import chess.pgn

from modules.position_list_node import PositionListNode
from modules.bcolors import bcolors

# minimum number of movies required for a puzzle to be considered complete
MIN_MOVES = 2

class Puzzle(object):
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

    def candidate_moves_annotations(self, candidate_moves):
        """ Returns the scores of the possible candidate moves
        """
        comment = ""
        for analysis in candidate_moves:
            comment += analysis.move_san
            if analysis.evaluation.mate:
                comment += " [mate in %d] " % analysis.evaluation.mate
            else:
                comment += " [%d] " % analysis.evaluation.cp
        return comment.strip()

    def to_pgn(self):
        fen = self.last_pos.fen()
        board = chess.Board(fen)
        game = chess.pgn.Game().from_board(board)
        
        # In the tactic the first to move is the one who lost
        result = '1-0' # result of the tactic not the game
        if board.turn: # turn return true if white
            result = '0-1'

        node = game.add_variation(self.last_move)
        position_list_node = self.position_list_node
        for m in position_list_node.move_list():
            node = node.add_variation(chess.Move.from_uci(m))
            node.comment = self.candidate_moves_annotations(
                position_list_node.candidate_moves
            )
            position_list_node = position_list_node.next_position
        for h in self.game.headers:
            game.headers[h] = self.game.headers[h]
        game.headers['PuzzleEngine'] = self.engine.name
        game.headers['PuzzleResult'] = result
        return game

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
