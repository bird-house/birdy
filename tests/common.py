# noqa: D100

import os
import pathlib


def resource_file(filepath):  # noqa: D103
    return os.path.join(test_directory(), "resources", filepath)


def test_directory():
    """Helper function to return path to the tests directory."""
    return os.path.dirname(__file__)


# These tests assume Emu is running on the localhost
URL_EMU = "http://localhost:5000/wps"
EMU_CAPS_XML = pathlib.Path(resource_file("wps_emu_caps.xml")).open("rb").read()
EMU_DESC_XML = pathlib.Path(resource_file("wps_emu_desc.xml")).open("rb").read()
