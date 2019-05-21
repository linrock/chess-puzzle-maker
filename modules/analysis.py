from chess.engine import SimpleEngine, Limit

from modules.fishnet import stockfish_command

engine = SimpleEngine.popen_uci(stockfish_command())


def compare_move_with_best_move(board, move, depth):
    info = engine.analyse(board, Limit(depth=depth))
    best_move = info["pv"][0]
    score = info["score"].white()
    print(board.san(best_move), score)
    info = engine.analyse(board, Limit(depth=depth), root_moves=[move])
    best_move = info["pv"][0]
    score = info["score"].white()
    print(board.san(best_move), score)
