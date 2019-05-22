from collections import namedtuple

from chess.engine import SimpleEngine, Limit

from modules.fishnet import stockfish_command

AnalyzedMove = namedtuple("AnalyzedMove", ["move", "move_san", "score"])

class AnalysisEngine(object):
    """ Light wrapper around chess.engine
    """
    engine: SimpleEngine = None

    def instance():
        if not AnalysisEngine.engine:
            AnalysisEngine.engine = SimpleEngine.popen_uci(stockfish_command())
        return AnalysisEngine.engine

    def quit():
        if AnalysisEngine.engine:
            AnalysisEngine.engine.quit()
            AnalysisEngine.engine = None


def analyze_position(self, board, depth) -> AnalyzedMove:
    info = self.engine.analyse(board, Limit(depth=depth))
    best_move = info["pv"][0]
    score = info["score"].white()
    analyzed_move = AnalyzedMove(best_move, board.san(best_move), score)
    return analyzed_move

def compare_move_with_best_move(board, move, depth):
    info = engine.analyse(board, Limit(depth=depth))
    best_move = info["pv"][0]
    score = info["score"].white()
    print(board.san(best_move), score)
    info = engine.analyse(board, Limit(depth=depth), root_moves=[move])
    best_move = info["pv"][0]
    score = info["score"].white()
    print(board.san(best_move), score)
