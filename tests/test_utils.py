import pytest
from unittest import TestCase

import tempfile
import base64

from birdy import utils


def test_fix_local_url():
    url = utils.fix_local_url('http://path/to/testfile.nc')
    assert url == 'http://path/to/testfile.nc'

    url = utils.fix_local_url('testfile.nc')
    assert url.startswith('file:///')
    assert url.endswith('testfile.nc')

    url = utils.fix_local_url('/tmp/data/testfile.nc')
    assert url == 'file:///tmp/data/testfile.nc'

    url = utils.fix_local_url('  /home/data/testfile.nc  ')
    assert url == 'file:///home/data/testfile.nc'

    url = utils.fix_local_url('../../testfile.nc')
    assert url.startswith('file:///')
    assert url.endswith('testfile.nc')

    url = utils.fix_local_url('  ../../testfile.nc  ')
    assert url.startswith('file:///')
    assert url.endswith('testfile.nc')

    # TODO: replace ~
    #url = utils.fix_local_url('~/data/testfile.nc')
    #nose.tools.ok_(False, url)


def test_encode():
    fp = tempfile.NamedTemporaryFile(delete=False)
    fp.write('hello')
    fp.close()

    content = utils.encode(fp.name, mimetypes=["application/xml"])
    assert content == 'hello'

    content = utils.encode(fp.name, mimetypes=["TEXT/PLAIN"])
    assert content == 'hello'

    content = utils.encode(fp.name, mimetypes=["application/x-netcdf"])
    assert content == base64.b64encode('hello')

    url = "file://%s" % fp.name
    content = utils.encode(url, mimetypes=["application/xml"])
    assert content == 'hello'
