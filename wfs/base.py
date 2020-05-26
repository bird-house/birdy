from ipyleaflet import GeoJSON, WidgetControl
from ipywidgets import HTML
from owslib.wfs import WebFeatureService
import json


class WFSGeojsonLayer(object):
    def __init__(self, url, wfs_version):
        # Connect to GeoServer WFS service.
        self._wfs = WebFeatureService(url, version=wfs_version)
        self._geojson = None
        self._widget = {}

    def create_layer(self, layer_typename, layer_style=None, source_map=None, widget_name='widget', property=None):
        """ Return an ipyleaflet GeoJSON layer from a geojson wfs request.

        Paremeters
        ----------
        layer_typename: string
          Typename of the layer to display. Listed as Layer_ID by get_layer_list().
          Must include namespace and layer name, seperated by a colon.

          ex: public:canada_forest_layer

        layer_style: dictionnary
        """

        computed_bbox = None
        if source_map:
            computed_bbox = self.get_coords(source_map.bounds)

        # Fetch and prepare data
        data = self._wfs.getfeature(typename=layer_typename, bbox=computed_bbox, outputFormat='JSON')
        self._geojson = json.loads(data.getvalue().decode())

        layer = GeoJSON(data=self._geojson, syle=layer_style)

        self.create_feature_property_widget(layer, source_map, widget_name, property)

        return layer

    def get_coords(self, coords):
        """Return formatted coordinates, from ipylealet format to owslib.wfs format.

        Parameters
        ----------
        coords: Tuple
          Coordinates as taken by the bounds method of an ipyleaflet Map.

        Returns
        -------
        Tuple
          Coordinates formated to WebFeatureService bounding box filter.
        """
        lon1 = coords[0][1]
        lat1 = coords[0][0]
        lon2 = coords[1][1]
        lat2 = coords[1][0]
        formatted_coordinates = (lon1, lat1, lon2, lat2)

        return formatted_coordinates

    def get_layer_list(self):
        return sorted(self._wfs.contents.keys())

    def get_layers_info(self):
        index = self.get_layer_list

        for layerID in index:
            layer = self._wfs[layerID]
            print('Layer ID:', layerID)
            print('Title:', layer.title)
            print('Boundaries:', layer.boundingBoxWGS84, '\n')

    def get_property_list(self, index=0):
        return self._geojson['features'][index]['properties']

    def _set_widget(self, widget_name, src_map, textbox, widget_position):
        if widget_name in self._widget:
            src_map.remove_control(self._widget[widget_name])

        self._widget[widget_name] = WidgetControl(widget=textbox,
                                                  position=widget_position,
                                                  min_width=120,
                                                  max_width=120)

        src_map.add_control(self._widget[widget_name])

    def create_feature_property_widget(self,
                                       layer,
                                       src_map,
                                       widget_name='widget',
                                       property=None,
                                       widget_position='bottomright'):

        textbox = HTML('''
            Click on a feature
        ''')
        textbox.layout.margin = '0px 20px 20px 20px'

        self._set_widget(widget_name, src_map, textbox, widget_position)

        def update_textbox(feature, **kwargs):
            key = list(feature['properties'].keys())[0]
            if property:
                key = property
            textbox.value = '''
                <h4>{}<h4>
                <b style="font-size:10px">{}<b>
            '''.format(key, feature['properties'][key])

        layer.on_click(update_textbox)
