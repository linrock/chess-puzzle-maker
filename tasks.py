from invoke import task
from puzzlemaker.fishnet import stockfish_command

@task
def test(c, unit=False, integration=False):
    """ Run all unit or integration tests
    """
    if unit:
        cmd = "python3 -m unittest test/unit/test_*.py"
    elif integration:
        cmd = "python3 -m unittest test/integration/test_*.py"
    else:
        cmd = "python3 -m unittest test/*/test_*.py"
    c.run(cmd, pty=True)


@task
def type_check(c):
    """ Check types
    """
    c.run("mypy --ignore-missing-imports --no-warn-no-return modules")

@task
def update_stockfish(c):
    """ Updates to the latest Stockfish version used by lichess
    """
    stockfish_command(update=True)

@task
def fetch_lichess(c, tournament_id='', game_id=''):
    """ Fetch all games played in a lichess tournament
    """
    if len(tournament_id):
        id = tournament_id
        c.run("curl https://lichess.org/api/tournament/%s/games > tournament.%s.pgn" % (id, id), pty=True)
    elif len(game_id):
        id = game_id
        c.run("curl https://lichess.org/game/export/%s > game.%s.pgn" % (id, id), pty=True)
