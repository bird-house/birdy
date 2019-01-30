from birdy import utils
from .common import resource_file
import six
from pathlib import Path


def test_is_url():
    assert utils.is_url("http://localhost:5000/wps")
    assert utils.is_url("file:///path/to/my/file.txt")
    assert not utils.is_url("myfile.txt")


def test_is_file():
    assert not utils.is_file(None)
    assert utils.is_file(resource_file('dummy.nc'))
    long_str = "".join('a' for i in range(260))
    assert not utils.is_file(long_str)
    assert utils.is_file(Path(resource_file('dummy.nc')))


def test_sanitize():
    assert utils.sanitize('output') == 'output'
    assert utils.sanitize('My Output 1') == 'my_output_1'
    assert utils.sanitize('a.b') == 'a_b'
    assert utils.sanitize('a-b') == 'a_b'


def test_delist():
    assert utils.delist(['one', 'two']) == ['one', 'two']
    assert utils.delist(['one', ]) == 'one'
    assert utils.delist('one') == 'one'


class TestEncode:
    nc = resource_file('dummy.nc')
    xml = resource_file('wps_emu_caps.xml')

    def test_str(self):
        s = 'just a string'
        assert utils.embed(s) == (s, 'utf-8')

    def test_local_fn(self):
        nc, enc = utils.embed(self.nc, 'application/x-netcdf')
        assert isinstance(nc, six.binary_type)
        assert enc == 'base64'

        xml, enc = utils.embed(self.xml, 'text/xml')
        assert isinstance(xml, six.string_types)
        assert enc == 'utf-8'

    def test_local_uri(self):
        xml, enc = utils.embed('file://' + self.xml, 'text/xml')
        assert isinstance(xml, six.string_types)

    def test_path(self):
        p = Path(self.nc)

        nc, enc = utils.embed(p, 'application/x-netcdf')
        assert isinstance(nc, six.binary_type)

    def test_file(self):
        with open(self.nc, 'rb') as fp:
            nc, enc = utils.embed(fp, 'application/x-netcdf')
            assert isinstance(nc, six.binary_type)
