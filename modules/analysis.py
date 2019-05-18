import chess.uci

from modules.fishnet import stockfish_command

engine = chess.uci.popen_engine(stockfish_command())
