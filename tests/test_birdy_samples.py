import pytest
from unittest import TestCase

from __init__ import SERVICE, Args, resource_file

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

    @pytest.mark.online
    def test_wordcount_http(self):
        self.args.identifier = 'wordcounter'
        self.args.text = 'http://birdy.readthedocs.org/en/latest/index.html'
        self.birdy.complex_inputs['text'] = ['text/plain']

        execution = self.birdy.execute(self.args)
        assert execution.isSucceded() is True

    @pytest.mark.online
    def test_wordcount_file(self):
        self.args.identifier = 'wordcounter'
        self.args.text = resource_file('the_great_gatsby.txt')
        self.birdy.complex_inputs['text'] = ['text/plain']

        execution = self.birdy.execute(self.args)
        assert execution.isSucceded() is True

    @pytest.mark.online
    def test_wordcount_remote_service(self):
        self.args.identifier = 'wordcounter'
        self.args.text = resource_file('the_great_gatsby.txt')
        birdy = Birdy('http://127.0.0.1:8094/wps')
        birdy.complex_inputs['text'] = ['text/plain']

        execution = birdy.execute(self.args)
        assert execution.isSucceded() is True
