from distutils.version import StrictVersion
from importlib import import_module
import six

if six.PY2:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve


class BaseConverter(object):
    mimetype = None

    # _default = None

    def __init__(self, output=None):
        """Instantiate the conversion class.

        Args:
            output (owslib.wps.Output): Output object to be converted.
        """
        self.output = output
        self.check_dependencies()

    def check_dependencies(self):
        pass

    def _check_import(self, name, package=None):
        """
        Args:
            name: module name to try to import
            package: package of the module
        """
        try:
            import_module(name, package)
        except ImportError as e:
            message = "Class {} has unmet dependencies: {}"
            raise type(e)(message.format(self.__name__, name))

    def convert(self):
        """Do the conversion from text or bytes to python object."""
        data = self.output.retrieveData()

        # Launch conversion
        return self.convert_data(data)

    def convert_data(self, data):
        """
        Args:
            data:
        """
        raise NotImplementedError


class TextConverter(BaseConverter):
    mimetype = "text/plain"

    def convert_data(self, data):
        """
        Args:
            data:
        """
        if isinstance(data, bytes):
            return data.decode("utf-8")
        elif isinstance(data, str):
            return data


class JSONConverter(BaseConverter):
    mimetype = "application/json"

    def convert_data(self, data):
        """
        Args:
            data:
        """
        import json

        return json.loads(data)


class GeoJSONConverter(BaseConverter):
    mimetype = "application/geojson"

    def check_dependencies(self):
        self._check_import("geojson")

    def convert_data(self, data):
        """
        Args:
            data:
        """
        import geojson

        return geojson.loads(data)


class Netcdf4Converter(BaseConverter):
    mimetype = "application/x-netcdf"

    def check_dependencies(self):
        self._check_import("netCDF4")
        from netCDF4 import getlibversion

        version = StrictVersion(getlibversion().split(" ")[0])
        if version < StrictVersion("4.5"):
            raise ImportError("netCDF4 library must be at least version 4.5")

    def convert_data(self, data):
        """
        Args:
            data:
        """
        import netCDF4

        try:
            # try OpenDAP url
            return netCDF4.Dataset(self.output.reference)
        except IOError:
            # download the file
            temp_file, _ = urlretrieve(self.output.reference)
            return netCDF4.Dataset(temp_file)


class ShpFionaConverter(BaseConverter):
    mimetype = "application/x-zipped-shp"

    def check_dependencies(self):
        self._check_import("fiona")

    def convert(self):
        raise NotImplementedError
        # import fiona
        # import io
        # return lambda x: fiona.open(io.BytesIO(x))


class ShpOgrConverter(BaseConverter):
    mimetype = "application/x-zipped-shp"

    def check_dependencies(self):
        self._check_import("ogr", package="osgeo")

    def convert(self):
        raise NotImplementedError
        # from osgeo import ogr
        # return ogr.Open


default_converters = {
    TextConverter.mimetype: TextConverter,
    JSONConverter.mimetype: JSONConverter,
    GeoJSONConverter.mimetype: GeoJSONConverter,
    Netcdf4Converter.mimetype: Netcdf4Converter,
    # 'application/x-zipped-shp': ShpConverter,
}
