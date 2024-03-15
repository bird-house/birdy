# noqa: D205,D400
"""
Dependencies Module
===================

Module for managing optional dependencies.

Example usage::

    >>> from birdy.dependencies import ipywidgets as widgets
"""

import warnings

from .exceptions import IPythonWarning

# TODO: we ignore warnings for now. They are only needed when birdy is used in a notebook,
# but we currently don't know how to handle this (see #89 and #138).
warnings.filterwarnings("ignore", category=IPythonWarning)

try:
    import ipywidgets
except ImportError:
    ipywidgets = None
    warnings.warn(
        "Jupyter Notebook is not supported. Please install *ipywidgets*.",
        IPythonWarning,
    )

try:
    import IPython
except ImportError:
    IPython = None
    warnings.warn("IPython is not supported. Please install *ipython*.", IPythonWarning)

try:
    import ipyleaflet
except ImportError:
    ipyleaflet = None
    warnings.warn(
        "Ipyleaflet is not supported. Please install *ipyleaflet*.", IPythonWarning
    )
