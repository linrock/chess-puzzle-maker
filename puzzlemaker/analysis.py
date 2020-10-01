from typing import List, Optional, Union
from collections import namedtuple
import glob
import shutil

from chess.engine import SimpleEngine, Limit, Score, EngineTerminatedError, InfoDict

from puzzlemaker.fishnet import stockfish_command
from puzzlemaker.logger import log
from puzzlemaker.colors import Color
from puzzlemaker.utils import sign

AnalyzedMove = namedtuple("AnalyzedMove", ["move", "move_san", "score"])


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
        if not AnalysisEngine.engine:
            return
        try:
            AnalysisEngine.engine.quit()
        except:
            pass
        AnalysisEngine.engine = None

    @staticmethod
    def best_move(board, depth) -> AnalyzedMove:
        info = AnalysisEngine._analyze(board, depth)
        if info.get("pv"):
            best_move = info["pv"][0]
        else:
            best_move = None
        score = info["score"].white()
        return AnalyzedMove(best_move, board.san(best_move), score)

    @staticmethod
    def best_moves(board, depth, multipv=3) -> List[AnalyzedMove]:
        best_moves = []
        infos = AnalysisEngine._analyze(board, depth, multipv=multipv)
        for info in infos:
            move = info["pv"][0]
            score = info["score"].white()
            best_moves.append(AnalyzedMove(move, board.san(move), score))
        return best_moves

    @staticmethod
    def evaluate_move(board, move, depth) -> AnalyzedMove:
        info = AnalysisEngine._analyze(board, depth, root_moves=[move])
        assert move == info["pv"][0]
        score = info["score"].white()
        return AnalyzedMove(move, board.san(move), score)

    @staticmethod
    def score(board, depth) -> Score:
        return AnalysisEngine.best_move(board, depth).score

    @staticmethod
    def _analyze(board, depth, **kwargs) -> Union[List[InfoDict], InfoDict]:
        try:
            info = AnalysisEngine.instance().analyse(board, Limit(depth=depth), **kwargs)
        except EngineTerminatedError:
            log(Color.RED, "Analysis engine crashed... restarting")
            AnalysisEngine.quit()
            info = AnalysisEngine._analyze(board, depth, **kwargs)
        return info


def ambiguous_best_move(scores: List[Score]) -> bool:
    """
    Looks at a list of candidate scores (best move first) to determine
    if there's a single best player move

    Returns True if a clear best move can't be determined based on these scores
    """
    if len(scores) <= 1:
        return False
    best_move_score = scores[0].score()
    second_best_move_score = scores[1].score()
    if (best_move_score is not None and second_best_move_score is not None):
        score_change = abs(second_best_move_score - best_move_score)
        if abs(best_move_score) < 50:
            # From equality, greater than 110 cp diff
            if score_change > 110:
                return False
        if best_move_score < 210:
            # Significant difference between best move and 2nd best
            if score_change > 250:
                return False
            # Slight advantage vs equality
            if abs(second_best_move_score) < 50 and score_change > 110:
                return False
            # Slight advantage vs slight disadvantage
            if sign(scores[0]) != sign(scores[1]) and score_change > 120:
                return False
            # Unclear if the best move leads to a decisive advantage
            return True
        if best_move_score < 1000:
            # If the best move is decisively better than the 2nd best move
            if best_move_score > 350 and second_best_move_score < 140:
                return False
            elif best_move_score - second_best_move_score > 500:
                return False
        if second_best_move_score > 90:
            return True
    if scores[0].is_mate():
        if scores[1].is_mate():
            if (scores[0].mate() > -1 and scores[1].mate() > -1):
                # More than one possible mate-in-1
                return True
        elif second_best_move_score:
            if second_best_move_score > 500:
                # 2nd best move is a decisive material advantage
                return True
    return False


def _stockfish_command() -> Optional[str]:
    cmd = stockfish_command()
    if shutil.which(cmd):
        return stockfish_command()
    local_stockfish_bins = glob.glob("./stockfish-*")
    if local_stockfish_bins:
        # matches 'stockfish-x86_64' in local dir after running build-stockfish.sh
        return local_stockfish_bins[0]
    else:
        return shutil.which("stockfish")
