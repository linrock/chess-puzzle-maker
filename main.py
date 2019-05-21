#!/usr/bin/env python3

""" Creates chess puzzles in PGN format from PGN files
"""

import argparse
import logging
import os
import sys

import chess
import chess.engine
import chess.pgn

from modules.logger import log_move
from modules.bcolors import bcolors
from modules.puzzle import Puzzle
from modules.utils import normalize_score, should_investigate
from modules.analysis import engine


parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument("games", metavar="GAMES", nargs="?", type=str, default="games.pgn",
                    help="A PGN file with games to scan for puzzles")

parser.add_argument("--output", metavar="OUTPUT_PGN", default="tactics.out.pgn",
                    help="An output pgn file")

# Chess engine settings
group = parser.add_argument_group('chess engine settings')
group.add_argument("--threads", metavar="THREADS", nargs="?", type=int, default=2,
                    help="number of engine threads")
group.add_argument("--memory", metavar="MEMORY", nargs="?", type=int, default=2048,
                    help="memory in MB to use for engine hashtables")
group.add_argument("--scan-depth", metavar="DEPTH", nargs="?", type=int, default=15,
                    help="depth for scanning a game for candidate puzzles")
group.add_argument("--search-depth", metavar="DEPTH", nargs="?", type=int, default=22,
                    help="depth for searching a position for candidate moves")

parser.add_argument("--quiet", dest="loglevel",
                    default=logging.DEBUG, action="store_const", const=logging.INFO,
                    help="substantially reduce the number of logged messages")
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
logging.getLogger("chess").setLevel(logging.WARNING)

all_games = open(settings.games, "r")

engine.configure({
  'Threads': settings.threads,
  'Hash': settings.memory,
  'Contempt': 0,
})

n_positions = 0   # number of positions considered
n_puzzles = 0     # number of puzzles generated
game_id = 0

while True:
    game = chess.pgn.read_game(all_games)
    if game == None:
        break
    game_id = game_id + 1 
    logging.debug(bcolors.MAGENTA + "\nGame ID: " + str(game_id) + bcolors.ENDC)
    logging.debug(bcolors.BLUE + str(game)  + bcolors.ENDC)
    
    prev_score = chess.engine.Cp(0)
    puzzles = []
    
    logging.debug(
        bcolors.DIM +
        ("Scanning game for puzzles (depth: %d)..." % settings.scan_depth) +
        bcolors.ENDC
    )
    # engine.ucinewgame()

    # Scan through the game, looking for possible puzzles
    node = game
    i = 0
    while not node.is_end():
        next_node = node.variation(0)
        next_board = next_node.board()
        info = engine.analyse(
            next_board,
            chess.engine.Limit(depth=settings.scan_depth)
        )
        cur_score = info["score"].white()
        board = node.board()
        highlight_move = False
        if should_investigate(prev_score, cur_score, board):
            highlight_move = True
            # Found a possible puzzle
            # don't check for move ambiguity if it's the first position in
            # the PGN since the PGN might be a puzzle instead of a game
            puzzle = Puzzle(
                board,
                next_node.move,
                check_ambiguity=i > 0
            )
            puzzles.append(puzzle)
        log_move(board, next_node.move, cur_score, highlight=highlight_move)
        prev_score = cur_score
        node = next_node
        i += 1

    n = len(puzzles)
    n_positions += n
    logging.debug(bcolors.YELLOW + ("# positions to consider as puzzles = %d" % n))
    if settings.scan_only:
        continue
    for i, puzzle in enumerate(puzzles):
        logging.debug(bcolors.MAGENTA + ("\nConsidering position %d of %d..." % (i+1, n)) + bcolors.ENDC)
        puzzle.generate(settings.search_depth)
        if puzzle.is_complete():
            puzzle_pgn = str(puzzle.export(pgn_headers=game.headers))
            logging.debug(bcolors.MAGENTA + "\nNEW PUZZLE GENERATED" + bcolors.ENDC)
            logging.info(bcolors.CYAN + puzzle_pgn + bcolors.ENDC)
            tactics_file = open(settings.output, "a")
            tactics_file.write(puzzle_pgn)
            tactics_file.write("\n\n")
            tactics_file.close()
            n_puzzles += 1

logging.debug(
    bcolors.MAGENTA +
    "\nGenerated %d puzzles from %d positions in %d games" %
    (n_puzzles, n_positions, game_id)
)
