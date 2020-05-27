from ipyleaflet import GeoJSON, WidgetControl
from ipywidgets import HTML
from owslib.wfs import WebFeatureService
import json


class WFSGeojsonLayer(object):
    """Create a connection to a WFS service capable of geojson output.

    This class is a small wrapper for ipylealet to facilitate the use of
    a WFS service, as well as provide some automation.

    Access to a WFS service is done through the owslib module and requires
    a geojson output capable WFS, which is then used to create an ipyleaflet
    GeoJSON layer.

    Parameters:
    -----------
    url: string
      The url of the WFS service

    wfs_version: string
      The version of the WFS service to use. Defaults to 2.0.0

    Returns
    -------
    WFSGeojsonLayer instance
      Instance from which the WFS layers can be created and then added to an
      ipyleaflet Map
    """

    def __init__(self, url, wfs_version='2.0.0'):
        self._wfs = WebFeatureService(url, version=wfs_version)
        self._geojson = None
        self._widgets = {}

    # # # # # # # # # # #
    # Utility functions #
    # # # # # # # # # # #

    def _get_first_property_key(self, feature):
        return list(feature['properties'].keys())[0]

    def _get_coords(self, coords):
        """Return formatted coordinates, from ipylealet format to owslib.wfs format.

        Parameters
        ----------
        coords: Tuple
          Coordinates as taken by the bounds method of an ipyleaflet Map.

        Returns
        -------
        Tuple
          Coordinates formatted to WebFeatureService bounding box filter.
        """
        lon1 = coords[0][1]
        lat1 = coords[0][0]
        lon2 = coords[1][1]
        lat2 = coords[1][0]
        formatted_coordinates = (lon1, lat1, lon2, lat2)

        return formatted_coordinates

    # # # # # # # # # # # # # # #
    # Layer creation function  #
    # # # # # # # # # # # # # # #

    def create_layer(self, layer_typename, source_map, layer_style=None, property=None):
        """ Return an ipyleaflet GeoJSON layer from a geojson wfs request.

        Requires the WFS service to be capable of geojson output.

        Parameters
        ----------
        layer_typename: string
          Typename of the layer to display. Listed as Layer_ID by get_layer_list().
          Must include namespace and layer name, separated  by a colon.

          ex: public:canada_forest_layer

        source_map: Map instance
            The map instance on which the layer is to be added

        layer_style: dictionnary
            ipyleaflet GeoJSON style format. See ipyleaflet documentation for more information

            ex: { 'color': 'white', 'opacity': 1, 'dashArray': '9', 'fillOpacity': 0.1, 'weight': 1 }

        property: string

        """

        automatic_bbox = self._get_coords(source_map.bounds)

        # Fetch and prepare data
        data = self._wfs.getfeature(typename=layer_typename, bbox=automatic_bbox, outputFormat='JSON')
        self._geojson = json.loads(data.getvalue().decode())

        layer = GeoJSON(data=self._geojson, style=layer_style)

        self.create_feature_property_widget(layer, source_map, 'main_widget', property)

        return layer

    # # # # # # # # # # # # # # # #
    # Layer information functions #
    # # # # # # # # # # # # # # # #

    def feature_properties_by_id(self, feature_id):
        """Return the properties of a feature

        The id field is usually the first field. Since the name is
        always different, this is the only assumption that can be
        made to automate this process. Hence, this will not work if
        the layer in question does not follow this formatting.

        Parameters
        ----------
        feature_id: int
          The feature id.

        Returns
        -------
        Dict
          A dictionary  of the layer's properties
        """
        for feature in self._geojson['features']:
            # The id field is usually the first field. Since the name is
            # always different, this is the only assumption that can be
            # made to automate this process.
            first_key = self._get_first_property_key(feature)
            current_feature_id = feature['properties'][first_key]

            if current_feature_id == feature_id:
                return feature['properties']

    @property
    def geojson(self):
        """Return the imported geojson data in a python object format.
        """
        return self._geojson

    @property
    def layer_list(self):
        """Return a simple layer list available to the WFS service

        Returns
        -------
        List
          A List of the WFS layers available
        """
        return sorted(self._wfs.contents.keys())

    @property
    def property_list(self):
        """Return a list containing the properties of the first feature.

        Retrieves the available properties for use subsequent use
        by the feature property widget

        Returns
        -------
        Dict
          A dictionary  of the layer properties
        """
        return self._geojson['features'][0]['properties']

    # # # # # # # # # # # # # # # # #
    # Property visualization widget #
    # # # # # # # # # # # # # # # # #

    def _set_widget(self, widget_name, src_map, textbox, widget_position):
        if widget_name in self._widgets:
            src_map.remove_control(self._widgets[widget_name])

        self._widgets[widget_name] = WidgetControl(widget=textbox,
                                                   position=widget_position,
                                                   min_width=120,
                                                   max_width=120)

        src_map.add_control(self._widgets[widget_name])

    def clear_property_widgets(self, src_map):
        """Remove all property widgets from a map.

        This function will remove the property widgets from a given map, without
        affecting other widgets

        Parameters
        ----------
        src_map: Map instance
          The map instance from which the widgets are to be removed
        """
        for widget in self._widgets:
            src_map.remove_control(self._widgets[widget])
        self._widgets.clear()

    def create_feature_property_widget(self,
                                       layer,
                                       src_map,
                                       widget_name,
                                       property=None,
                                       widget_position='bottomright'):
        """Create a visualization widget for a specific feature property

        Once the widget is created, click on a map feature to have the information
        appear in the corresponding box.

        To replace the default widget that get created by the create_layer() function,
        set the  widget_name parameter to 'main_widget'

        Widgets create by this function are unique by their widget_name variable.

        Parameters
        ----------
        layer: WFS Layer
          A WFS layer created by this module, or any ipyleaflet GeoJSON layer

        src_map: Map instance
          The map instance used in the current notebook

        widget_name: string
          Name of the widget. Must be unique or will overwrite existing widget

        property: string
          The property key to be used by the widget. Use the property_list() function
          to get a list of the available properties

        widget_position: string
          Position on the map for the widget. Choose between ‘bottomleft’, ‘bottomright’, ‘topleft’, or ‘topright’

        """

        textbox = HTML('''
            Click on a feature
        ''')
        textbox.layout.margin = '20px 20px 20px 20px'

        self._set_widget(widget_name, src_map, textbox, widget_position)

        def _update_textbox(properties=None, **kwargs):
            # The check for properties is necessary because of a bug in ipylealet.
            # On_click registers twice, which causes a TypeError
            # See https://github.com/jupyter-widgets/ipyleaflet/issues/373
            if properties is None:
                return

            key = list(properties.keys())[0]
            if property:
                key = property
            textbox.value = '''
                <h4>{}<h4>
                <b style="font-size:10px">{}<b>
            '''.format(key, properties[key])

        layer.on_click(_update_textbox)
