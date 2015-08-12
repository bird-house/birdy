from unittest import TestCase
import nose.tools
from nose import SkipTest

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
