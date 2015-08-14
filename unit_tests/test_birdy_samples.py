from unittest import TestCase
import nose.tools
from nose import SkipTest
from nose.plugins.attrib import attr

from __init__ import SERVICE, Args

from birdy import Birdy

class BirdySampleTestCase(TestCase):
    """
    test command line client birdy:

    See: http://dustinrcollins.com/testing-python-command-line-apps
    """

    def setUp(self):
        self.birdy = Birdy(SERVICE)

    @attr('online')
    @attr('slow')
    def test_wordcount(self):
        args = Args()
        args.debug = True
        args.identifier = 'wordcount'
        args.text = 'http://birdy.readthedocs.org/en/latest/index.html'
        args.output = None

        execution = self.birdy.execute(args)
        nose.tools.ok_(execution.isSucceded())
