#!/usr/bin/env python
"""Tests for `birdy` package."""

import pathlib
from importlib.util import find_spec


def test_package_metadata():
    """Test the package metadata."""
    project = find_spec("birdy")

    assert project is not None
    assert project.submodule_search_locations is not None
    location = project.submodule_search_locations[0]

    metadata = pathlib.Path(location).resolve().joinpath("__init__.py")

    with metadata.open() as f:
        contents = f.read()
        assert """Carsten Ehbrecht""" in contents
        assert '__email__ = "ehbrecht@dkrz.de"' in contents
        assert '__version__ = "0.10.0"' in contents
