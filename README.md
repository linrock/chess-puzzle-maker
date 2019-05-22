# Chess puzzle maker

This program creates chess puzzles from positions with clear sequences of best moves.
It looks for positions where a player can:

* Checkmate the opponent in a forced sequence
* Convert a position into a material advantage after a mistake by the opponent
* Equalize a losing position after a mistake by the opponent

Give it a PGN with any number of games or positions and it will look for positions to convert into puzzles:

`./make_puzzles.py --pgn games.pgn`

Or give it a position (FEN) and it will try to create a puzzle:

`./make_puzzles.py --fen "6rr/1k3p2/1pb1p1np/p1p1P2R/2P3R1/2P1B3/P1BK1PP1/8 b - - 5 26"`

For a list of options:

`./make_puzzles.py -h`


## Requirements

This requires Python 3 and a UCI-compatible chess engine such as Stockfish.

Install the required python libraries:

`pip3 install -r requirements.txt`

Download an official Stockfish binary from the [Stockfish website](https://stockfishchess.org/download/) and make sure `stockfish` is available in your `$PATH`

Or run `inv update-stockfish` to get the latest multi-variant Stockfish fork used by Lichess.


### Output

By default, the resulting puzzles will be printed in PGN format to standard output while errors and log messages are printed to standard error.

If you want to write the puzzles to a file, redirect standard output:

`./make_puzzles.py --pgn games.pgn >> puzzles.pgn`

An example PGN output:

```
[FEN "6rr/1k3p2/1pb1p1np/p1p1P2R/2P3R1/2P1B3/P1BK1PP1/8 b - - 5 26"]
[PuzzleCategory "Material"]
[PuzzleEngine "Stockfish 2018-11-29 64 Multi-Variant"]
[PuzzleWinner "Black"]
[SetUp "1"]

26... Nxe5   { Nxe5  (-168) }
27.   Rxg8   { Rxg8  (-166) Rgh4 (-251)  Re4 (-351) }
27... Nxc4+  { Nxc4+ (-178) Rxg8 ( 382)  Nf3+ (479) }
28.   Kd3    { Kd3   (-155) Ke2  (-183)  Kd1 (-285) }
28... Nb2+   { Nb2+  (-178) Rxg8 ( 211)  Ne5+ (344) }
29.   Ke2    { Kd2   (-164) Ke2  (-174)             }
```

Each move is annotated with the scores for the best possible moves from that position
as determined by the chess engine.


### Tests

You can run the whole test suite with

`inv test`


### Acknowledgements

This program is based on:

* [Python-Puzzle-Creator](https://github.com/clarkerubber/Python-Puzzle-Creator) by [@clarkerubber](https://github.com/clarkerubber)
* [pgn-tactics-generator](https://github.com/vitogit/pgn-tactics-generator) by [@vitogit](https://github.com/vitogit)
