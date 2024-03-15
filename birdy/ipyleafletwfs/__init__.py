# noqa: D205,D400
"""
IpyleafletWFS Module
====================

This module facilitates the use of a WFS service through the ipyleaflet module in jupyter notebooks.
It uses owslib to get a geojson out of a WFS service, and then creates an ipyleaflet GeoJSON layer with it.

Dependencies
------------

Ipyleaflet and Ipywidgets dependencies are included in the requirements_extra.txt, at the root of this repository.
To install::

    $ pip install -r requirements_extra.txt

Use
---

This module is to be used inside a jupyter notebook, either with a standard server or through vscode/pycharm.
There are notebook examples which show how to use this module and what can be done with it.

The WFS request is filtered by the extent of the visible map, to make large layers easier to work with.
Using the on-map 'Refresh WFS layer' button will make a new request for the current extent.

.. warning::
    WFS requests and GeoJSON layers are costly operations to process and render.
    Trying to load lake layers at the nationwide extent may take a long time and probably crash.
    The more dense and complex the layer, the more zoomed-in the map extent should be.
"""

from .base import IpyleafletWFS  # noqa: F401
