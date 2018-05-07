import pytest

from .common import WpsTestCase

from birdy.wpsparser import (
    parse_wps_description,
    parse_process_help,
    is_complex_data,
    parse_default,
    parse_description
)


class WPSParserTestCase(WpsTestCase):

    def test_parse_wps_description(self):
        # TODO: add test with unicode characters e.a:
        # http://geoprocessing.demo.52north.org:8080/52n-wps-webapp-3.3.1/WebProcessingService?Request=GetCapabilities&Service=WPS  # noqa
        result = parse_wps_description(self.wps)
        assert result == 'Emu: WPS processes for testing and demos.'

    def test_parse_process_help(self):
        process = self.wps.processes[0]
        result = parse_process_help(process)
        assert result == "Hello World: Welcome user and say hello ... [100%% quick response]"

    def test_is_complex_data(self):
        process = self.wps.processes[0]
        for input in process.dataInputs:
            assert is_complex_data(input) is False

    def test_parse_default(self):
        process = self.wps.processes[0]
        for input in process.dataInputs:
            assert parse_default(input) is False

    def test_parse_description(self):
        process = self.wps.processes[0]
        for input in process.dataInputs:
            result = parse_description(input)
            assert len(result) > 0
