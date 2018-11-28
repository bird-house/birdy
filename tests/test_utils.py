from birdy import utils


def test_is_url():
    assert utils.is_url("http://localhost:5000/wps")
    assert utils.is_url("file:///path/to/my/file.txt")
    assert not utils.is_url("myfile.txt")


def test_make_identifier():
    assert utils.make_identifier('output') == 'output'
    assert utils.make_identifier('My Output 1') == 'my_output_1'


def test_delist():
    assert utils.delist(['one', 'two']) == ['one', 'two']
    assert utils.delist(['one', ]) == 'one'
    assert utils.delist('one') == 'one'
