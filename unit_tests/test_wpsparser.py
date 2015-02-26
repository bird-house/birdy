import nose.tools
from nose import SkipTest
from nose.plugins.attrib import attr

from __init__ import TESTDATA, WpsTestCase

from birdy.wpsparser import (
    parse_wps_description,
    parse_process_help,
    is_complex_data,
    parse_default,
    parse_description
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

    @attr('online')
    def test_is_complex_data(self):
        process = self.wps.describeprocess('helloworld')
        for input in process.dataInputs:
            nose.tools.ok_(is_complex_data(input) == False)

    @attr('online')
    def test_parse_default(self):
        raise SkipTest
        process = self.wps.describeprocess('helloworld')
        for input in process.dataInputs:
            nose.tools.ok_(False, parse_default(input))

    @attr('online')
    def test_parse_description(self):
        process = self.wps.describeprocess('helloworld')
        for input in process.dataInputs:
            result = parse_description(input)
            nose.tools.ok_(len(result), result)
        
