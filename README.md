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

And have a version of Stockfish available in your `$PATH`:

* Download an official Stockfish binary from the [Stockfish website](https://stockfishchess.org/download/)
* Or run `inv update-stockfish` to get the latest multi-variant Stockfish fork used by Lichess


## Creating puzzles

Created puzzles are printed in PGN format to standard output
while errors and log messages are printed to standard error.

If you want to write created puzzles to a file, redirect standard output:

`./make_puzzles.py --pgn games.pgn >> puzzles.pgn`

An example PGN output:

```
[FEN "6rr/1k3p2/1pb1p1np/p1p1P2R/2P3R1/2P1B3/P1BK1PP1/8 b - - 5 26"]
[PuzzleCategory "Material"]
[PuzzleEngine "Stockfish 2018-11-29 64 Multi-Variant"]
[PuzzleWinner "Black"]
[SetUp "1"]

26... Nxe5   { Nxe5  [-1.68] }
27.   Rxg8   { Rxg8  [-1.66] Rgh4 [-2.51]  Re4  [-3.51] }
27... Nxc4+  { Nxc4+ [-1.78] Rxg8 [ 3.82]  Nf3+ [ 4.79] }
28.   Kd3    { Kd3   [-1.55] Ke2  [-1.83]  Kd1  [-2.85] }
28... Nb2+   { Nb2+  [-1.78] Rxg8 [ 2.11]  Ne5+ [ 3.44] }
29.   Ke2    { Kd2   [-1.64] Ke2  [-1.74]               }
```

Each move in the puzzle is annotated with the best 3 candidate moves
considered by the chess engine.


## Examples

To scan a PGN for positions that might be candidate puzzles without
investigating any of the positions:

`./make_puzzles.py --scan-only --pgn games.pgn`

To start at the n-th PGN in a file:

`./make_puzzles.py --start-index 1234 --pgn games.pgn`

To fetch a Lichess game and save it as a PGN:

`inv fetch-lichess -g 12345`

To fetch all games from a Lichess tournament and save the games to PGN:

`inv fetch-lichess -t 67890`

You can run the whole test suite with:

`inv test`


## Acknowledgements

This program is based on:

* [Python-Puzzle-Creator](https://github.com/clarkerubber/Python-Puzzle-Creator) by [@clarkerubber](https://github.com/clarkerubber)
* [pgn-tactics-generator](https://github.com/vitogit/pgn-tactics-generator) by [@vitogit](https://github.com/vitogit)
