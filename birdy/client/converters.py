from distutils.version import StrictVersion
from importlib import import_module
import six
from . import notebook as nb
import tempfile
from pathlib import Path
from owslib.wps import Output
import warnings


if six.PY2:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve


class BaseConverter(object):
    mimetype = None
    extensions = []
    priority = 1
    nested = False

    def __init__(self, output=None, path=None):
        """Instantiate the conversion class.

        Args:
            output (owslib.wps.Output): Output object to be converted.
        """
        self.path = path or tempfile.mkdtemp()
        self.output = output
        self.check_dependencies()
        if isinstance(output, Output):
            self.url = output.reference
            self._file = None
        elif isinstance(output, (str, Path)):
            self._file = Path(output)
            if not self.file.exists():
                raise FileNotFoundError(output)

    @property
    def file(self):
        if self._file is None:
            self.output.writeToDisk(path=self.path)
            self._file = Path(self.output.filePath)
        return self._file

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
            raise type(e)(message.format(self.__class__.__name__, name))

    def convert(self):
        return self.file.read_text(encoding='utf8')


class TextConverter(BaseConverter):
    mimetype = "text/plain"
    extensions = ['txt', 'csv']


class JSONConverter(BaseConverter):
    mimetype = "application/json"
    extensions = ['json', ]

    def convert(self):
        """
        Args:
            data:
        """
        import json
        with open(self.file) as f:
            return json.load(f)


class GeoJSONConverter(BaseConverter):
    mimetype = "application/vnd.geo+json"
    extensions = ['geojson', ]

    def check_dependencies(self):
        self._check_import("geojson")

    def convert(self):
        import geojson
        with open(self.file) as f:
            return geojson.load(f)


class MetalinkConverter(BaseConverter):
    mimetype = "application/metalink+xml; version=3.0"
    extensions = ['metalink', 'meta4', ]
    nested = True

    def check_dependencies(self):
        self._check_import("metalink.download")

    def convert(self):
        import metalink.download as md
        files = md.get(self.url, path=self.path)
        return files


class Netcdf4Converter(BaseConverter):
    mimetype = "application/x-netcdf"
    extensions = ['nc', ]

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
            return netCDF4.Dataset(self.url)
        except IOError:
            # download the file
            return netCDF4.Dataset(self.file)


class XarrayConverter(Netcdf4Converter):
    priority = 2

    def check_dependencies(self):
        Netcdf4Converter.check_dependencies(self)
        self._check_import('xarray')

    def convert(self):
        import xarray as xr
        try:
            # try OpenDAP url
            return xr.open_dataset(self.url)
        except IOError:
            # download the file
            return xr.open_dataset(self.file)


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
    extensions = ['png', ]

    def check_dependencies(self):
        return nb.is_notebook()

    def convert(self):
        from birdy.dependencies import IPython
        return IPython.display.Image(self.url)


class ZipConverter(BaseConverter):
    mimetype = 'application/zip'
    extensions = ['zip', ]
    nested = True

    def convert(self):
        import zipfile
        with zipfile.ZipFile(self.file) as z:
            z.extractall(path=self.path)
            return [str(Path(self.path) / fn) for fn in z.namelist()]


def _find_converter(mimetype=None, extension=None, converters=()):
    """Return a list of compatible converters ordered by priority.
    """
    select = []
    for obj in converters:
        if (mimetype == obj.mimetype) or (extension in obj.extensions):
            select.append(obj)

    select.sort(key=lambda x: x.priority, reverse=True)
    return select


def find_converter(obj, converters):
    """Find converters for a WPS output or a file on disk."""
    if isinstance(obj, Output):
        mimetype = obj.mimeType
        extension = Path(obj.fileName or '').suffix[1:]
    elif isinstance(obj, (str, Path)):
        mimetype = None
        extension = Path(obj).suffix[1:]
    else:
        raise NotImplementedError

    return _find_converter(mimetype, extension, converters=converters)


def convert(output, path, converters=None):
    """Convert a file to an object.

    Parameters
    ----------
    output : owslib.wps.Output, Path, str
      Item to convert to an object.
    path : str, Path
      Path on disk where temporary files are stored.
    converters : sequence of BaseConverter subclasses
      Converter classes to search within for a match.

    Returns
    -------
    objs
      Python object or path to file if no converter was found.
    """
    if converters is None:
        converters = BaseConverter.__subclasses__()

    convs = find_converter(output, converters)

    for cls in convs:
        try:
            converter = cls(output, path=path)
            out = converter.convert()
            if converter.nested:  # Then the output is a list of files.
                out = [convert(o, path) for o in out]
            return out

        except ImportError:
            pass

    warnings.warn(UserWarning("No converter was found."))
    return output.reference
