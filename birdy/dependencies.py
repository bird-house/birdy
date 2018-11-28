# -*- coding: utf-8 -*-

"""
This module is used to manage optional dependencies.

Example usage::

    from birdy.dependencies import ipywidgets as widgets
"""

import warnings
from .exceptions import IPythonWarning

warnings.filterwarnings('default', category=IPythonWarning)

try:
    import ipywidgets
except ImportError:
    ipywidgets = None
    warnings.warn('Jupyter Notebook is not supported. Please install *ipywidgets*.', IPythonWarning)

try:
    import IPython
except ImportError:
    IPython = None
    warnings.warn('IPython is not supported. Please install *ipython*.', IPythonWarning)
