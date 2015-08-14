from unittest import TestCase
import nose.tools
from nose import SkipTest
from nose.plugins.attrib import attr

from os.path import join, dirname
__testdir__ = dirname(__file__)

from __init__ import SERVICE, Args

from birdy import Birdy

class BirdySampleTestCase(TestCase):
    """
    test command line client birdy:

    See: http://dustinrcollins.com/testing-python-command-line-apps
    """

    def setUp(self):
        self.birdy = Birdy(SERVICE)
        self.args = Args()
        self.args.debug = True
        self.args.identifier = None
        self.args.output = None

    @attr('online')
    @attr('slow')
    def test_wordcount_remote(self):
        self.args.identifier = 'wordcount'
        self.args.text = 'http://birdy.readthedocs.org/en/latest/index.html'
        self.birdy.complex_inputs['text'] = ['text/plain']

        execution = self.birdy.execute(self.args)
        nose.tools.ok_(execution.isSucceded())

    @attr('online')
    @attr('slow')
    def test_wordcount_local(self):
        self.args.identifier = 'wordcount'
        self.args.text = join(__testdir__, 'the_great_gatsby.txt')
        self.birdy.complex_inputs['text'] = ['text/plain']

        execution = self.birdy.execute(self.args)
        nose.tools.ok_(execution.isSucceded())
