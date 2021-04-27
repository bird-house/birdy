# noqa: D100

from birdy.client import notebook


def test_is_notebook():  # noqa: D103
    # we expect True or False but no exception
    notebook.is_notebook()
