from invoke import task

@task
def test(c, test_type=None):
    """ Run all unit or integration tests
    """
    if test_type:
        c.run("python3 -m unittest test/%s/test_*.py" % test_type, pty=True)
    else:
        c.run("python3 -m unittest test/*/test_*.py", pty=True)
