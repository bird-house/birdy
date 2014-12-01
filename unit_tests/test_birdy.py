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
    def test_with_empty_args(self):
        """
        User passes no args, should fail with SystemExit
        """                                    
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])
            
    @attr('online')
    def test_birdy(self):
        raise SkipTest
        from birdy import main
        nose.tools.ok_(False, 'birdy needs some work')
