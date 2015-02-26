from unittest import TestCase
import nose.tools
from nose import SkipTest
from nose.plugins.attrib import attr

from __init__ import TESTDATA, SERVICE

from birdy import Birdy

class BirdyTestCase(TestCase):
    """
    test command line client birdy:

    See: http://dustinrcollins.com/testing-python-command-line-apps
    """

    def setUp(self):
        self.birdy = Birdy(SERVICE)

    @attr('online')
    def test_with_empty_args(self):
        """
        User passes no args, should fail with SystemExit
        """
        parser = self.birdy.create_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([])
            
    @attr('online')
    def test_help(self):
        """
        Help messages ends with SystemExit

        TODO: overwrite exit method? See: http://bugs.python.org/issue9938
        """
        parser = self.birdy.create_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args('-h'.split())

    @attr('online')
    def test_inout(self):
        """
        Try inout command
        """
        raise SkipTest
        parser = self.birdy.create_parser()
        args = parser.parse_args('inout'.split())
        nose.tools.ok_(args.identifier == 'inout', args)
        nose.tools.ok_(args.output == 'output', args)
        
