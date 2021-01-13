import os


def resource_file(filepath):
    return os.path.join(test_directory(), "resources", filepath)


def test_directory():
    """Helper function to return path to the tests directory"""
    return os.path.dirname(__file__)


# These tests assume Emu is running on the localhost
URL_EMU = "http://localhost:5000/wps"
EMU_CAPS_XML = open(resource_file("wps_emu_caps.xml"), "rb").read()
EMU_DESC_XML = open(resource_file("wps_emu_desc.xml"), "rb").read()
