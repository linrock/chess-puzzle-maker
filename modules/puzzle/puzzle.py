import os
import json
import logging

import chess
import chess.pgn

from modules.puzzle.position_list import PositionList
from modules.bcolors import bcolors


class Puzzle(object):
    def __init__(self, last_pos, last_move, game_id, engine, info_handler, game, strict):
        self.last_pos = last_pos.copy()
        self.last_move = last_move
        self.game_id = game_id
        last_pos.push(last_move)
        self.position_list = PositionList(last_pos, engine, info_handler, strict = strict)
        self.game = game

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'category': self.position_list.category(),
            'last_pos': self.last_pos.fen(),
            'last_move': self.last_move.uci(),
            'move_list': self.position_list.move_list()
        }

    def to_pgn(self):
        fen = self.last_pos.fen()
        board = chess.Board(fen)
        game = chess.pgn.Game().from_board(board)
        
        # In the tactic the first to move is the one who lost
        result = '1-0' # result of the tactic not the game
        if board.turn: # turn return true if white
            result = '0-1'

        node = game.add_variation(self.last_move)
        for m in self.position_list.move_list():
            node = node.add_variation(chess.Move.from_uci(m))

        for h in self.game.headers:
            game.headers[h] = self.game.headers[h]
        game.headers['Result'] = result
        return game

    def color(self):
        return self.position_list.position.turn

    def is_complete(self):
        return (self.position_list.is_complete(
                self.position_list.category(), 
                self.color(), 
                True, 
                self.position_list.material_difference()
            )
            and not self.position_list.ambiguous()
            and len(self.position_list.move_list()) > 2)

    def generate(self, depth):
        self.position_list.generate(depth)
        if self.is_complete():
            logging.debug(bcolors.OKGREEN + "Puzzle is complete" + bcolors.ENDC)
        else:
            logging.debug(bcolors.FAIL + "Puzzle incomplete" + bcolors.ENDC)

    def category(self):
        return self.position_list.category()
