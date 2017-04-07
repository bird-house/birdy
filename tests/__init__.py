import os
import logging

from unittest import TestCase

SERVICE = "http://localhost:8094/wps"


def resource_file(filepath):
    return os.path.join(test_directory(), 'resources', filepath)


def test_directory():
    """Helper function to return path to the tests directory"""
    return os.path.dirname(__file__)


class Args(object):
    """
    Namespace to collect parsed arguments
    """
    pass


class WpsTestCase(TestCase):
    """
    Base TestCase class, sets up a wps
    """

    @classmethod
    def setUpClass(cls):
        from owslib.wps import WebProcessingService
        cls.wps = WebProcessingService(SERVICE, verbose=False, skip_caps=True)
        with open(resource_file('wps_emu_caps.xml'), 'rb') as fp:
            xml = fp.read()
            cls.wps.getcapabilities(xml=xml)
