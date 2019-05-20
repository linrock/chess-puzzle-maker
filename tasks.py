from invoke import task

@task
def test(c, test_type):
    """ Run all unit or integration tests
    """
    c.run("python3 -m unittest test/%s/test_*.py" % test_type)
