from distutils.version import StrictVersion
from importlib import import_module
import six
from . import notebook as nb
import tempfile

if six.PY2:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve


class BaseConverter(object):
    mimetype = None
    extensions = []

    # _default = None

    def __init__(self, output=None, path=None):
        """Instantiate the conversion class.

        Args:
            output (owslib.wps.Output): Output object to be converted.
        """
        self.path = path or tempfile.mkdtemp()
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
    extensions = ['txt', ]

    def convert_data(self, data):
        """
        Args:
            data:
        """
        if isinstance(data, bytes):
            return data.decode("utf-8")
        elif isinstance(data, str):
            return data


class CSVConverter(BaseConverter):
    mimetype = "text/plain"
    extensions = ['csv', ]

    def convert_data(self, data):
        """
        Args:
            data:
        """
        import csv
        data = data.decode("utf-8") if isinstance(data, bytes) else data
        return csv.reader(data.splitlines())


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
    mimetype = "application/vnd.geo+json"

    def check_dependencies(self):
        self._check_import("geojson")

    def convert_data(self, data):
        """
        Args:
            data:
        """
        import geojson
        return geojson.loads(data)


class MetalinkConverter(BaseConverter):
    mimetype = "application/metalink+xml"

    def check_dependencies(self):
        self._check_import("metalink.download")

    def convert(self, data):
        """
        Args:
            data:
        """
        import metalink.download as md
        return md.get


class Netcdf4Converter(BaseConverter):
    mimetype = "application/x-netcdf"

    def check_dependencies(self):
        self._check_import("netCDF4")
        from netCDF4 import getlibversion

        version = StrictVersion(getlibversion().split(" ")[0])
        if version < StrictVersion("4.5"):
            raise ImportError("netCDF4 library must be at least version 4.5")

    def convert(self):
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
            self.output.writeToDisk(path=self.path)
            return netCDF4.Dataset(self.output.filePath)


class XarrayConverter(Netcdf4Converter):

    def check_dependencies(self):
        Netcdf4Converter.check_dependencies(self)
        self._check_import('xarray')

    def convert(self):
        import xarray as xr
        try:
            # try OpenDAP url
            return xr.open_dataset(self.output.reference)
        except IOError:
            # download the file
            self.output.writeToDisk(path=self.path)
            return xr.open_dataset(self.output.filePath)


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


# TODO: Add test for this.
class ImageConverter(BaseConverter):
    mimetype = 'image/png'

    def check_dependencies(self):
        return nb.is_notebook()

    def convert(self):
        from birdy.dependencies import IPython

        url = self.output.reference
        return IPython.display.Image(url)


class ZipConverter(BaseConverter):
    mimetype = 'application/zip'

    def convert(self):
        import zipfile

        self.output.writeToDisk(path=self.path)
        with zipfile.ZipFile(self.output.filePath) as z:
            return z


default_converters = {
    TextConverter.mimetype: [TextConverter, ],
    JSONConverter.mimetype: [JSONConverter, ],
    GeoJSONConverter.mimetype: [GeoJSONConverter, ],
    Netcdf4Converter.mimetype: [XarrayConverter, Netcdf4Converter],
    ImageConverter.mimetype: [ImageConverter, ],
    ZipConverter.mimetype: [ZipConverter, ]
    # 'application/x-zipped-shp': [ShpConverter, ],
}
