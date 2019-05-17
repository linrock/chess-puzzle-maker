import logging
import os
from collections import namedtuple

import chess

from modules.bcolors import bcolors
from modules.utils import material_difference

Analysis = namedtuple("Analysis", ["move", "evaluation"])

class PositionList(object):
    def __init__(self, position, engine, info_handler, player_turn=True, best_move=None, evaluation=None, strict = True):
        self.position = position.copy()
        self.engine = engine
        self.info_handler = info_handler
        self.player_turn = player_turn
        self.best_move = best_move
        self.evaluation = evaluation
        self.next_position = None
        self.candidate_moves = []
        self.strict = strict

    def move_list(self):
        if self.next_position is None or self.next_position.ambiguous() or self.next_position.position.is_game_over():
            if self.best_move is not None:
                return [self.best_move.bestmove.uci()]
            else:
                return []
        else:
            return [self.best_move.bestmove.uci()] + self.next_position.move_list()

    def category(self):
        if self.next_position is None:
            if self.position.is_game_over():
                return 'Mate'
            else:
                return 'Material'
        else:
            return self.next_position.category()

    def generate(self, depth):
        logging.debug(bcolors.WARNING + str(self.position) + bcolors.ENDC)
        logging.debug(bcolors.WARNING + self.position.fen() + bcolors.ENDC)
        logging.debug(bcolors.OKBLUE + ('Material difference:  %d' % self.material_difference()))
        logging.debug(bcolors.OKBLUE + ("# legal moves:        %d" % len(self.position.legal_moves)) + bcolors.ENDC)
        has_best = self.evaluate_best(depth)
        if not self.player_turn:
            self.next_position.generate(depth)
            return
        self.evaluate_candidate_moves(depth)
        if has_best and not self.ambiguous() and not self.game_over():
            logging.debug(bcolors.OKGREEN + "Going deeper:")
            logging.debug("   Ambiguous: " + str(self.ambiguous()))
            logging.debug("   Has best move: " + str(has_best) + bcolors.ENDC)
            self.next_position.generate(depth)
        else:
            logging.debug(bcolors.WARNING + "Not going deeper:")
            logging.debug("   Ambiguous: " + str(self.ambiguous()))
            logging.debug("   Game over: " + str(self.game_over()))
            logging.debug("   Has best move: " + str(has_best) + bcolors.ENDC)

    def evaluate_best(self, depth):
        logging.debug(bcolors.OKGREEN + "Evaluating best move...")
        self.engine.position(self.position)
        self.best_move = self.engine.go(depth=depth)
        if self.best_move.bestmove is not None:
            self.evaluation = self.info_handler.info["score"][1]
            self.next_position = PositionList(self.position.copy(),
                self.engine,
                self.info_handler,
                not self.player_turn,
                strict = self.strict
            )
            self.next_position.position.push(self.best_move.bestmove)
            logging.debug(bcolors.OKGREEN + "Best move: " + self.best_move.bestmove.uci() + bcolors.ENDC)
            if self.evaluation.mate:
                logging.debug(bcolors.OKBLUE + "   Mate: " + str(self.evaluation.mate) + bcolors.ENDC)
            else:
                logging.debug(bcolors.OKBLUE + "   CP: " + str(self.evaluation.cp))
            return True
        else:
            logging.debug(bcolors.FAIL + "No best move!" + bcolors.ENDC)
            return False

    # Analyze the best possible moves from the current position
    def evaluate_candidate_moves(self, depth):
        multipv = min(3, len(self.position.legal_moves))
        logging.debug(bcolors.OKGREEN + ("Evaluating best %d moves..." % multipv) + bcolors.ENDC)
        self.engine.setoption({ "MultiPV": multipv })
        self.engine.position(self.position)
        self.engine.go(depth=depth)

        info = self.engine.info_handlers[0].info
        for i in range(multipv):
            move = info["pv"].get(i + 1)[0]
            evaluation = info["score"].get(i + 1)
            self.candidate_moves.append(Analysis(move, evaluation))

        for analysis in self.candidate_moves:
            logging.debug(bcolors.OKGREEN + "Move: " + str(analysis.move.uci()) + bcolors.ENDC)
            if analysis.evaluation.mate:
                logging.debug(bcolors.OKBLUE + "   Mate: " + str(analysis.evaluation.mate))
            else:
                logging.debug(bcolors.OKBLUE + "   CP: " + str(analysis.evaluation.cp))
        self.engine.setoption({ "MultiPV": 1 })

    def material_difference(self):
        return material_difference(self.position)

    def material_count(self):
        return chess.pop_count(self.position.occupied)

    def is_complete(self, category, color, first_node, first_val):
        if self.next_position is not None:
            if ((category == 'Mate' and not self.ambiguous())
                or (category == 'Material' and self.next_position.next_position is not None)):
                return self.next_position.is_complete(category, color, False, first_val)
        
        if category == 'Material':
            if color:
                if (self.material_difference() > 0.2 
                    and abs(self.material_difference() - first_val) > 0.1 
                    and first_val < 2
                    and self.evaluation.mate is None
                    and self.material_count() > 6):
                    return True
                else:
                    return False
            else:
                if (self.material_difference() < -0.2 
                    and abs(self.material_difference() - first_val) > 0.1
                    and first_val > -2
                    and self.evaluation.mate is None
                    and self.material_count() > 6):
                    return True
                else:
                    return False
        else:
            if self.position.is_game_over() and self.material_count() > 6:
                return True
            else:
                return False

    # Return True if it's unclear whether there's a single best player move
    def ambiguous(self):
        # If strict == False then it will generate more tactics but  more ambiguous
        move_number = 1 if self.strict == True else 2
        if len(self.candidate_moves) > 1:
            best_move_score = self.candidate_moves[0].evaluation.cp
            second_best_move_score = self.candidate_moves[1].evaluation.cp
            if (best_move_score is not None and second_best_move_score is not None):
                # Unclear if the best move leads to a decisive advantage
                if best_move_score < 210:
                    return True
                if second_best_move_score > 90:
                    # If the best move is decisively better than the 2nd best move
                    if best_move_score - second_best_move_score > 500:
                        return False
                    else:
                        return True
            if self.candidate_moves[0].evaluation.mate:
                if self.candidate_moves[1].evaluation.mate:
                    if (self.candidate_moves[0].evaluation.mate > -1 and self.candidate_moves[1].evaluation.mate > -1):
                        # More than one possible mate-in-1
                        return True
                elif self.candidate_moves[1].evaluation.cp is not None:
                    if self.candidate_moves[1].evaluation.cp > 200:
                        return True
        return False

    def game_over(self):
        return self.next_position.position.is_game_over()
