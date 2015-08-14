from unittest import TestCase
import nose.tools
from nose import SkipTest
from nose.plugins.attrib import attr

from __init__ import TESTDATA, SERVICE

from birdy import Birdy

class Args(object):
    """
    Namespace to collect parsed arguments
    """
    pass

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
        try:
            parser.parse_args([], namespace=Args)
        except SystemExit as e:
            nose.tools.ok_(e.code > 0, e)
        else:
            nose.tools.ok_(False, 'no error message')
            
    @attr('online')
    def test_help(self):
        """
        Help messages ends with SystemExit

        TODO: overwrite exit method? See: http://bugs.python.org/issue9983
        """
        parser = self.birdy.create_parser()
        try:
            args = parser.parse_args(['-h'], namespace=Args)
        except SystemExit as e:
            nose.tools.ok_(e.code == 0, e)

    @attr('online')
    def test_inout_command(self):
        parser = self.birdy.create_parser()
        try:
            parser.parse_args('inout -h'.split(), namespace=Args)
        except SystemExit as e:
            nose.tools.ok_(e.code == 0, e)
        nose.tools.ok_(Args.identifier == 'inout')

    @attr('online')
    def test_invalid_command(self):
        parser = self.birdy.create_parser()
        try:
            parser.parse_args('fake_cmd -h'.split(), namespace=Args)
        except SystemExit as e:
            nose.tools.ok_(e.code > 0, e)
        else:
            nose.tools.ok_(False, 'no error message')

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
