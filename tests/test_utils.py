from unittest import TestCase
import nose.tools
from nose import SkipTest

import tempfile
import base64

from birdy import utils


def test_fix_local_url():
    url = utils.fix_local_url('http://path/to/testfile.nc')
    nose.tools.ok_(url == 'http://path/to/testfile.nc', url)

    url = utils.fix_local_url('testfile.nc')
    nose.tools.ok_(url.startswith('file:///'), url)
    nose.tools.ok_(url.endswith('testfile.nc'), url)

    url = utils.fix_local_url('/tmp/data/testfile.nc')
    nose.tools.ok_(url == 'file:///tmp/data/testfile.nc', url)

    url = utils.fix_local_url('  /home/data/testfile.nc  ')
    nose.tools.ok_(url == 'file:///home/data/testfile.nc', url)

    url = utils.fix_local_url('../../testfile.nc')
    nose.tools.ok_(url.startswith('file:///'), url)
    nose.tools.ok_(url.endswith('testfile.nc'), url)

    url = utils.fix_local_url('  ../../testfile.nc  ')
    nose.tools.ok_(url.startswith('file:///'), url)
    nose.tools.ok_(url.endswith('testfile.nc'), url)

    # TODO: replace ~
    #url = utils.fix_local_url('~/data/testfile.nc')
    #nose.tools.ok_(False, url)


def test_encode():
    fp = tempfile.NamedTemporaryFile(delete=False)
    fp.write('hello')
    fp.close()

    content = utils.encode(fp.name, mimetypes=["application/xml"])
    nose.tools.ok_(content == 'hello')

    content = utils.encode(fp.name, mimetypes=["TEXT/PLAIN"])
    nose.tools.ok_(content == 'hello')

    content = utils.encode(fp.name, mimetypes=["application/x-netcdf"])
    nose.tools.ok_(content == base64.b64encode('hello'), content)

    url = "file://%s" % fp.name
    content = utils.encode(url, mimetypes=["application/xml"])
    nose.tools.ok_(content == 'hello')
