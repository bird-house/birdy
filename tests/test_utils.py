from birdy import utils


def test_is_url():
    assert utils.is_url("http://localhost:5000/wps")
    assert utils.is_url("file:///path/to/my/file.txt")
    assert not utils.is_url("myfile.txt")


def test_sanitize():
    assert utils.sanitize('output') == 'output'
    assert utils.sanitize('My Output 1') == 'my_output_1'
    assert utils.sanitize('a.b') == 'a_b'
    assert utils.sanitize('a-b') == 'a_b'


def test_delist():
    assert utils.delist(['one', 'two']) == ['one', 'two']
    assert utils.delist(['one', ]) == 'one'
    assert utils.delist('one') == 'one'
