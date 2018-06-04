from birdy import utils


def test_is_url():
    assert utils.is_url("http://localhost:5000/wps")
    assert utils.is_url("file:///path/to/my/file.txt")
    assert not utils.is_url("myfile.txt")
