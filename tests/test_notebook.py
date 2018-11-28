from birdy.client import notebook


def test_is_notebook():
    # we excpect True or False but no exception
    notebook.is_notebook()
