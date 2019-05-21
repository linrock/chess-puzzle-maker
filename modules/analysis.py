import chess.engine

from modules.fishnet import stockfish_command

engine = chess.engine.SimpleEngine.popen_uci(stockfish_command())
# engine.info_handlers.append(chess.uci.InfoHandler())
