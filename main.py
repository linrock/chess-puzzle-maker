#!/usr/bin/env python3

""" Creates chess puzzles in PGN format from PGN files
"""

import argparse
import logging
import os
import sys

import chess
import chess.uci
import chess.pgn

from modules.bcolors import bcolors
from modules.puzzle import Puzzle
from modules.utils import fullmove_string, normalize_score, should_investigate
from modules.analysis import engine


parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument("threads", metavar="THREADS", nargs="?", type=int, default=2,
                    help="number of engine threads")
parser.add_argument("memory", metavar="MEMORY", nargs="?", type=int, default=4096,
                    help="memory in MB to use for engine hashtables")
parser.add_argument("--depth", metavar="DEPTH", nargs="?", type=int, default=15,
                    help="stockfish depth for scanning for candidate puzzles")
parser.add_argument("--quiet", dest="loglevel",
                    default=logging.DEBUG, action="store_const", const=logging.INFO,
                    help="substantially reduce the number of logged messages")
parser.add_argument("--games", metavar="GAMES", default="games.pgn",
                    help="A specific pgn with games")
parser.add_argument("--output", metavar="OUTPUT_PGN", default="tactics.out.pgn",
                    help="An output pgn file")
parser.add_argument("--strict", metavar="STRICT", default=True,
                    help="If False then it will be generate more tactics but maybe a little ambiguous")
parser.add_argument("--scan-only", default=False, action="store_true",
                    help="Only scan for possible puzzles. Don't analyze positions")
settings = parser.parse_args()
try:
    # Optionally fix colors on Windows and in journals if the colorama module
    # is available.
    import colorama
    wrapper = colorama.AnsiToWin32(sys.stdout)
    if wrapper.should_wrap():
        sys.stdout = wrapper.stream
except ImportError:
    pass

logging.basicConfig(format="%(message)s", level=settings.loglevel, stream=sys.stdout)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
logging.getLogger("chess").setLevel(logging.WARNING)

engine.setoption({
  'Threads': settings.threads,
  'Hash': settings.memory,
  'Contempt': 0,
})
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

all_games = open(settings.games, "r")
game_id = 0

while True:
    game = chess.pgn.read_game(all_games)
    if game == None:
        break
    node = game

    game_id = game_id + 1 
    logging.debug(bcolors.HEADER + "\nGame ID: " + str(game_id) + bcolors.ENDC)
    logging.debug(bcolors.WARNING + str(game)  + bcolors.ENDC)
    
    prev_score = chess.uci.Score(0, None)
    puzzles = []
    
    logging.debug(
        bcolors.DIM +
        ("Scanning game for puzzles (depth: %d)..." % settings.depth) +
        bcolors.ENDC
    )
    engine.ucinewgame()

    # Scan through the game, looking for possible puzzles
    while not node.is_end():
        next_node = node.variation(0)
        next_board = next_node.board()
        engine.position(next_board)
        engine.go(depth=settings.depth)
        cur_score = normalize_score(next_board, info_handler.info["score"][1])
        # import pdb; pdb.set_trace()
        board = node.board()
        log_str = bcolors.GREEN
        log_str += ("%s%s" % (fullmove_string(board), board.san(next_node.move))).ljust(15)
        if cur_score.mate is not None:
            log_str += bcolors.BLUE + ("   Mate: " + str(cur_score.mate)).ljust(12)
        else:
            log_str += bcolors.BLUE + ("   CP: " + str(cur_score.cp)).ljust(12)
        if should_investigate(prev_score, cur_score, board):
            # Found a possible puzzle
            log_str += bcolors.WARNING + "   Investigate!" + bcolors.ENDC
            puzzle = Puzzle(
                board,
                next_node.move,
                game,
                settings.strict
            )
            puzzles.append(puzzle)
        logging.debug(log_str + bcolors.ENDC)
    
        prev_score = cur_score
        node = next_node

    n = len(puzzles)
    logging.debug(bcolors.WARNING + ("# positions to consider as puzzles = %d" % n))
    if settings.scan_only:
        continue
    for i, puzzle in enumerate(puzzles):
        logging.debug("")
        logging.debug(bcolors.HEADER + ("Considering position %d of %d..." % (i+1, n)) + bcolors.ENDC)
        # use depth 22 to explore puzzle positions
        puzzle.generate()
        if puzzle.is_complete():
            puzzle_pgn = str(puzzle.to_pgn())
            logging.debug(bcolors.HEADER + "NEW PUZZLE GENERATED" + bcolors.ENDC)
            logging.info(bcolors.BLUE + puzzle_pgn + bcolors.ENDC)
            tactics_file = open(settings.output, "a")
            tactics_file.write(puzzle_pgn)
            tactics_file.write("\n\n")
            tactics_file.close()

