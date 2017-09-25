import pytest
from unittest import TestCase

from .common import SERVICE, Args

from birdy import Birdy


class BirdyTestCase(TestCase):
    """
    test command line client birdy:

    See: http://dustinrcollins.com/testing-python-command-line-apps
    """

    def setUp(self):
        self.birdy = Birdy(SERVICE)

    @pytest.mark.online
    def test_with_empty_args(self):
        """
        User passes no args, should fail with SystemExit
        """
        parser = self.birdy.create_parser()
        try:
            parser.parse_args([], namespace=Args)
        except SystemExit as e:
            assert e.code > 0
        else:
            assert False

    @pytest.mark.online
    def test_help(self):
        """
        Help messages ends with SystemExit

        TODO: overwrite exit method? See: http://bugs.python.org/issue9983
        """
        parser = self.birdy.create_parser()
        try:
            parser.parse_args(['-h'], namespace=Args)
        except SystemExit as e:
            assert e.code == 0

    @pytest.mark.online
    def test_inout_command(self):
        parser = self.birdy.create_parser()
        try:
            parser.parse_args('inout -h'.split(), namespace=Args)
        except SystemExit as e:
            assert e.code == 0
        assert Args.identifier == 'inout'

    @pytest.mark.online
    def test_bbox_command(self):
        parser = self.birdy.create_parser()
        try:
            parser.parse_args('bbox -h'.split(), namespace=Args)
        except SystemExit as e:
            assert e.code == 0
        assert Args.identifier == 'bbox'

    @pytest.mark.online
    def test_invalid_command(self):
        parser = self.birdy.create_parser()
        try:
            parser.parse_args('fake_cmd -h'.split(), namespace=Args)
        except SystemExit as e:
            assert e.code > 0
        else:
            raise Exception('no error message')
