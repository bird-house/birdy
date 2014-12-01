import nose.tools
from nose import SkipTest
from nose.plugins.attrib import attr

from __init__ import TESTDATA

def test_birdy():
    from birdy import main
    nose.tools.ok_(False, 'birdy needs some work')
