import nose.tools
from unittest import TestCase
from nose import SkipTest
from nose.plugins.attrib import attr

from __init__ import TESTDATA, SERVICE

from birdy import create_parser

class CommandLineTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    
    See: http://dustinrcollins.com/testing-python-command-line-apps
    """

    @classmethod
    def setUpClass(cls):
        from owslib.wps import WebProcessingService
        wps = WebProcessingService(SERVICE, verbose=False, skip_caps=False)
        cls.parser = create_parser(wps)

class BirdyTestCase(CommandLineTestCase):
    @attr('online')
    def test_with_empty_args(self):
        """
        User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])
            
    @attr('online')
    def test_help(self):
        """
        Help messages ends with SystemExit

        TODO: overwrite exit method? See: http://bugs.python.org/issue9938
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args('-h'.split())

    @attr('online')
    def test_wget(self):
        """
        Try wget command
        """
        args = self.parser.parse_args('wget'.split())
        nose.tools.ok_(args.identifier == 'wget', args)
        nose.tools.ok_(args.output == 'output', args)
        
