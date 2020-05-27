# wfs-ipyleaflet

This module is meant to facilitate the use of a WFS service through the ipyleaflet module in jupyter notebooks

In essence, this module uses owslib to get a geojson out of a WFS service, and then create an ipyleaflet GeoJSON layer with it.

## Use

This module is meant to be used inside a jupyter notebook, either with a standard server or through vscode.

There is a notebook example, wfs-geojson-layer.ipynb, which shows how to use this module and what can be done with it.

The WFS request is filtered by the extent of the visible map, to make large layers easier to work with. 
A new request (re-creating the layer) will be needed if the map view is moved outside of the first bounds.

## Known issues

The on_click method for GeoJSON layers causes a typeError when used in jupyter notebook. It has already been reported: https://github.com/jupyter-widgets/ipyleaflet/issues/373

We get no such errors (at least visibly) when using the example notebook in vscode, but there appears to be no functionnality loss in jupyter
notebook, appart from the visual disturbance.

The workaround found in the above linked issue has been applied here and therefore should not be visible.