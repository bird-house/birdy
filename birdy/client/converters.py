# noqa: D100

import tempfile
from collections.abc import Sequence
from distutils.version import StrictVersion
from importlib import import_module
from pathlib import Path
from typing import Union

from owslib.wps import Output

from birdy.utils import is_opendap_url

from . import notebook as nb


class BaseConverter:  # noqa: D101
    mimetypes = ()
    extensions = ()
    priority = None
    nested = False

    def __init__(self, output=None, path=None, verify=True):
        """Instantiate the conversion class.

        Parameters
        ----------
        output: owslib.wps.Output
          Output object to be converted.
        """
        self.path = path or tempfile.mkdtemp()
        self.output = output
        self.verify = verify
        self.check_dependencies()
        if isinstance(output, Output):
            self.url = output.reference
            self._file = None
        elif isinstance(output, (str, Path)):
            self.url = output
            self._file = Path(output)
        else:
            raise NotImplementedError

    @property
    def file(self):
        """Return output Path object. Download from server if not found."""
        if self._file is None:
            self.output.writeToDisk(path=self.path, verify=self.verify)
            self._file = Path(self.output.filePath)
        return self._file

    @property
    def data(self):
        """Return the data from the remote output in memory."""
        if self._file is not None:
            return self.file.read_bytes()
        else:
            return self.output.retrieveData()

    def check_dependencies(self):  # noqa: D102
        pass

    def _check_import(self, name, package=None):
        """Check if libraries can be imported.

        Parameters
        ----------
        name: str
          module name to try to import
        package: str
          package of the module
        """
        try:
            import_module(name, package)
        except ImportError as e:
            message = f"Class {self.__class__.__name__} has unmet dependencies: {name}"
            raise type(e)(message)

    def convert(self):
        """To be subclassed."""
        raise NotImplementedError


class GenericConverter(BaseConverter):  # noqa: D101
    priority = 0

    def convert(self):
        """Return raw bytes memory representation."""
        return self.data


class TextConverter(BaseConverter):  # noqa: D101
    mimetypes = ["text/plain"]
    extensions = ["txt", "csv", "md", "rst"]
    priority = 1

    def convert(self):
        """Return text content."""
        return self.file.read_text(encoding="utf8")


# class HTMLConverter(BaseConverter):
#     """Create HTML cell in notebook."""
#     mimetype = "text/html"
#     extensions = ['html', ]
#
#     def check_dependencies(self):
#         return nb.is_notebook()
#
#     def convert(self):
#         from birdy.dependencies import ipywidgets as widgets
#         from birdy.dependencies import IPython
#
#         w = widgets.HTML(value=self.file.read_text(encoding='utf8'))
#         IPython.display.display(w)


class JSONConverter(BaseConverter):  # noqa: D101
    mimetypes = ["application/json"]
    extensions = ["json"]
    priority = 1

    def convert(self):  # noqa: D102
        import json

        with open(self.file) as f:
            return json.load(f)


class GeoJSONConverter(BaseConverter):  # noqa: D101
    mimetypes = ["application/geo+json", "application/vnd.geo+json"]
    extensions = ["json", "geojson"]
    priority = 2

    def check_dependencies(self):  # noqa: D102
        self._check_import("geojson")

    def convert(self):  # noqa: D102
        import geojson

        with open(self.file) as f:
            return geojson.load(f)


class MetalinkConverter(BaseConverter):  # noqa: D101
    mimetypes = [
        "application/metalink+xml; version=3.0",
        "application/metalink+xml; version=4.0",
    ]
    extensions = ["metalink", "meta4"]
    nested = True
    priority = 1

    def check_dependencies(self):  # noqa: D102
        self._check_import("metalink.download")

    def convert(self):  # noqa: D102
        from metalink import download as md

        files = md.get(self.url, path=self.path, segmented=False)
        return files


class Netcdf4Converter(BaseConverter):  # noqa: D101
    mimetypes = ["application/x-netcdf"]
    extensions = ["nc", "nc4"]
    priority = 1

    def check_dependencies(self):  # noqa: D102
        self._check_import("netCDF4")
        from netCDF4 import getlibversion

        version = StrictVersion(getlibversion().split(" ")[0])
        if version < StrictVersion("4.5"):
            raise ImportError("netCDF4 library must be at least version 4.5")

    def convert(self):  # noqa: D102
        import netCDF4

        # Try to access with OpenDAP url to avoid a download
        if is_opendap_url(self.url):
            return netCDF4.Dataset(self.url)

        # Download the file and open the local copy
        return netCDF4.Dataset(self.file)


class XarrayConverter(BaseConverter):  # noqa: D101
    mimetypes = ["application/x-netcdf"]
    extensions = ["nc", "nc4"]
    priority = 2

    def check_dependencies(self):  # noqa: D102
        Netcdf4Converter.check_dependencies(self)
        self._check_import("xarray")

    def convert(self):  # noqa: D102
        import xarray as xr

        # Try to access with OpenDAP url to avoid a download
        if is_opendap_url(self.url):
            return xr.open_dataset(self.url)

        # Download the file and open the local copy
        return xr.open_dataset(self.file)


# TODO: Add test for this.
class ShpFionaConverter(BaseConverter):  # noqa: D101
    mimetypes = ["application/x-zipped-shp"]
    priority = 1

    def check_dependencies(self):  # noqa: D102
        ShpOgrConverter.check_dependencies(self)
        self._check_import("fiona")

    def convert(self):  # noqa: D102
        import io  # isort: skip
        import fiona  # isort: skip

        return lambda x: fiona.open(io.BytesIO(x))


# TODO: Add test for this.
class ShpOgrConverter(BaseConverter):  # noqa: D101
    mimetypes = ["application/x-zipped-shp"]
    extensions = ["zip"]
    priority = 2

    def check_dependencies(self):  # noqa: D102
        self._check_import("ogr", package="osgeo")

    def convert(self):  # noqa: D102
        from osgeo import ogr

        return ogr.Open


# TODO: Add test for this. Probably can be applied to jpeg/jpg/gif but needs notebook testing
class ImageConverter(BaseConverter):  # noqa: D101
    mimetypes = ["image/png"]
    extensions = ["png"]
    priority = 1

    def check_dependencies(self):  # noqa: D102
        return nb.is_notebook()

    def convert(self):  # noqa: D102
        from birdy.dependencies import IPython

        return IPython.display.Image(self.url)


class GeotiffRioxarrayConverter(BaseConverter):  # noqa: D101
    mimetypes = ["image/tiff; subtype=geotiff"]
    extensions = ["tiff", "tif"]
    priority = 3

    def check_dependencies(self):  # noqa: D102
        self._check_import("rioxarray")

    def convert(self):  # noqa: D102
        import xarray  # isort: skip
        import rioxarray  # noqa

        return xarray.open_dataarray(self.file, engine="rasterio")


# TODO: Add test for this.
class GeotiffGdalConverter(BaseConverter):  # noqa: D101
    mimetypes = ["image/tiff; subtype=geotiff"]
    extensions = ["tiff", "tif"]
    priority = 1

    def check_dependencies(self):  # noqa: D102
        self._check_import("gdal", package="osgeo")

    def convert(self):  # noqa: D102
        import io  # isort: skip
        from osgeo import gdal  # isort: skip

        return lambda x: gdal.Open(io.BytesIO(x))


class ZipConverter(BaseConverter):  # noqa: D101
    mimetypes = ["application/zip"]
    extensions = ["zip"]
    nested = True
    priority = 1

    def convert(self):  # noqa: D102
        import zipfile

        with zipfile.ZipFile(self.file) as z:
            z.extractall(path=self.path)
            return [str(Path(self.path) / fn) for fn in z.namelist()]


def _find_converter(mimetype=None, extension=None, converters=()):
    """Return a list of compatible converters ordered by priority."""
    select = [GenericConverter]
    for obj in converters:
        if (mimetype in obj.mimetypes) or (extension in obj.extensions):
            select.append(obj)

    select.sort(key=lambda x: x.priority, reverse=True)
    return select


def find_converter(obj, converters):
    """Find converters for a WPS output or a file on disk."""
    if isinstance(obj, Output):
        mimetype = obj.mimeType
        extension = Path(obj.fileName or "").suffix[1:]
    elif isinstance(obj, (str, Path)):
        mimetype = None
        extension = Path(obj).suffix[1:]
    else:
        raise NotImplementedError

    return _find_converter(mimetype, extension, converters=converters)


def convert(
    output: Union[Output, Path, str],
    path: Union[str, Path],
    converters: Sequence[BaseConverter] = None,
    verify: bool = True,
):
    """Convert a file to an object.

    Parameters
    ----------
    output : owslib.wps.Output, Path, str
      Item to convert to an object.
    path : str, Path
      Path on disk where temporary files are stored.
    converters : sequence of BaseConverter subclasses
      Converter classes to search within for a match.
    verify : bool


    Returns
    -------
    objs
      Python object or file's content as bytes.
    """
    # Get all converters
    if converters is None:
        converters = all_subclasses(BaseConverter)

    # Find converters matching mime type or extension.
    convs = find_converter(output, converters)

    # Try converters in order of priority
    for cls in convs:
        try:
            converter = cls(output, path=path, verify=verify)
            out = converter.convert()
            if converter.nested:  # Then the output is a list of files.
                out = [convert(o, path) for o in out]
            return out

        except (ImportError, NotImplementedError):
            pass


def all_subclasses(cls):
    """Return all subclasses of a class."""
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )
