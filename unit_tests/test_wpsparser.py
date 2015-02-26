import nose.tools
from nose import SkipTest
from nose.plugins.attrib import attr

from __init__ import TESTDATA, WpsTestCase

from birdy.wpsparser import (
    parse_wps_description,
    parse_process_help
    )

class WPSParserTestCase(WpsTestCase):

    @attr('online')
    def test_parse_wps_description(self):
        result = parse_wps_description(self.wps)
        nose.tools.ok_('Emu' in result, result)

    @attr('online')
    def test_parse_process_help(self):
        process = self.wps.describeprocess('helloworld')
        result = parse_process_help(process)
        nose.tools.ok_('Hello' in result, result)
        
