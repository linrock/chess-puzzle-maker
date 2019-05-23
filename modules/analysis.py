from typing import List
from collections import namedtuple
import shutil

from chess.engine import SimpleEngine, Limit, Score

from modules.fishnet import stockfish_command

AnalyzedMove = namedtuple("AnalyzedMove", ["move", "move_san", "score"])

def _stockfish_command() -> str:
    cmd = stockfish_command()
    if shutil.which(cmd):
        return stockfish_command()
    else:
        return shutil.which("stockfish")

class AnalysisEngine(object):
    """ Light wrapper around chess.engine
    """
    engine: SimpleEngine = None

    @staticmethod
    def instance() -> SimpleEngine:
        if not AnalysisEngine.engine:
            AnalysisEngine.engine = SimpleEngine.popen_uci(_stockfish_command())
        return AnalysisEngine.engine

    @staticmethod
    def name() -> str:
        return AnalysisEngine.instance().id["name"]

    @staticmethod
    def quit():
        if AnalysisEngine.engine:
            AnalysisEngine.engine.quit()
            AnalysisEngine.engine = None

    def best_move(board, depth) -> AnalyzedMove:
        info = AnalysisEngine.instance().analyse(board, Limit(depth=depth))
        best_move = info["pv"][0]
        score = info["score"].white()
        return AnalyzedMove(best_move, board.san(best_move), score)

    def best_moves(board, depth, multipv=3) -> List[AnalyzedMove]:
        best_moves = []
        infos = AnalysisEngine.instance().analyse(board, Limit(depth=depth), multipv=multipv)
        for info in infos:
            move = info["pv"][0]
            score = info["score"].white()
            best_moves.append(AnalyzedMove(move, board.san(move), score))
        return best_moves

    def evaluate_move(board, move, depth) -> AnalyzedMove:
        info = AnalysisEngine.instance().analyse(board, Limit(depth=depth), root_moves=[move])
        assert move == info["pv"][0]
        score = info["score"].white()
        return AnalyzedMove(move, board.san(move), score)

    def score(board, depth) -> Score:
        info = AnalysisEngine.instance().analyse(board, Limit(depth=depth))
        return info["score"].white()
