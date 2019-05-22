#!/usr/bin/env python3

""" Creates chess puzzles from PGN files and FEN strings
"""

import argparse
import logging
import sys

from chess import Board
import chess.pgn

from modules.bcolors import bcolors
from modules.puzzle import Puzzle
from modules.puzzle_finder import find_puzzle_candidates
from modules.analysis import AnalysisEngine


parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

group = parser.add_argument_group('data inputs')
group.add_argument("--fen", metavar="FEN", nargs="?", type=str, default=None,
                    help="A FEN position from which to generate a puzzle")
group.add_argument("--pgn", metavar="PGN", nargs="?", type=str, default=None,
                    help="A PGN file with games to scan for puzzles")

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

parser.add_argument("--start-index", metavar="INDEX", type=int, default=0,
                    help="Start at the n-th game in a PGN (starting at 0)")
parser.add_argument("--quiet", dest="loglevel",
                    default=logging.DEBUG, action="store_const", const=logging.INFO,
                    help="substantially reduce the number of logged messages")
parser.add_argument("--scan-only", default=False, action="store_true",
                    help="Only scan for possible puzzles. Don't analyze positions")

if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(0)

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

engine = AnalysisEngine.instance()
engine.configure({
  'Threads': settings.threads,
  'Hash': settings.memory,
  'Contempt': 0,
})

logging.basicConfig(format="%(message)s", level=settings.loglevel, stream=sys.stderr)
logging.getLogger("chess").setLevel(logging.WARNING)

def print_puzzle_pgn(puzzle, pgn_headers=None):
    puzzle_pgn = puzzle.to_pgn(pgn_headers=pgn_headers)
    logging.debug(bcolors.MAGENTA + "NEW PUZZLE GENERATED\n" + bcolors.ENDC)
    print(bcolors.CYAN + puzzle_pgn + "\n\n" + bcolors.ENDC)


# load a FEN and try to create a puzzle from it

if settings.fen:
    puzzle = Puzzle(Board(settings.fen))
    puzzle.generate(depth=settings.search_depth)
    if puzzle.is_complete():
        print_puzzle_pgn(puzzle)
    engine.quit()
    exit(0)


# load games from a PGN and scan them for puzzles

n_positions = 0   # number of positions considered
n_puzzles = 0     # number of puzzles generated
game_id = 0
pgn = open(settings.pgn, "r")

while game_id < settings.start_index:
    game = chess.pgn.read_game(pgn)
    if game == None:
        exit(0)
    game_id += 1

while True:
    game = chess.pgn.read_game(pgn)
    if game == None:
        break
    logging.debug(bcolors.MAGENTA + "\nGame index: " + str(game_id) + bcolors.ENDC)
    logging.debug(bcolors.BLUE + str(game)  + bcolors.ENDC)
    puzzles = find_puzzle_candidates(game, scan_depth=settings.scan_depth)
    n = len(puzzles)
    logging.debug(bcolors.YELLOW + ("# positions to consider: %d" % n))
    if settings.scan_only:
        continue
    for i, puzzle in enumerate(puzzles):
        logging.debug(
            bcolors.MAGENTA +
            ("\nConsidering position %d of %d..." % (i+1, n)) +
            bcolors.ENDC
        )
        puzzle.generate(settings.search_depth)
        if puzzle.is_complete():
            print_puzzle_pgn(puzzle, pgn_headers=game.headers)
            n_puzzles += 1
    game_id += 1
    n_positions += n

logging.debug(
    bcolors.MAGENTA +
    "\nGenerated %d puzzles from %d positions in %d games" %
    (n_puzzles, n_positions, game_id)
)
engine.quit()
