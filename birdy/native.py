"""
The :func:`import_wps` function *imports* on the fly a python module whose
functions call WPS processes. The module is generated at runtime based on the
process description provided by the WPS server. Calling a function sends
an `execute` request to the server, which returns a response.

The response is parsed to convert the outputs in native python whenever possible.
`LiteralOutput` objects (string, float, integer, boolean) are automatically
converted to their native format. For `ComplexOutput`, the module can either
return a link to the output files stored on the server (default), or try to
convert the outputs to a python object based on their mime type. So for example,
if the mime type is 'application/json', the module would read the remote output
file and `json.loads` it to return a `dict`.

The behavior of the module can be configured using the :class:`config`, see its
docstring for more information.

Example
-------
If a WPS server with a simple `hello` process is running on the local host on port 5000::

  >>> from birdy import import_wps
  >>> emu = import_wps('http://localhost:5000/')
  >>> emu.hello
  <function birdy.native.hello(name)>
  >>> print(emu.hello.__doc__)
  ""
  Just says a friendly Hello. Returns a literal string output with Hello plus the inputed name.

  Parameters
  ----------
  name : string
      Please enter your name.

  Returns
  -------
  output : string
      A friendly Hello from us.

  ""

  # Call the function
  >>> emu.hello('stranger')
  'Hello stranger'

"""
import dateutil.parser
from distutils.version import StrictVersion
import urllib
from copy import copy

import six
import types
from importlib import import_module
from collections import OrderedDict

from owslib.util import ServiceException
from owslib.wps import WPS_DEFAULT_VERSION, SYNC, ComplexDataInput
from owslib.wps import WebProcessingService
from boltons.funcutils import FunctionBuilder

from birdy.utils import delist


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
            temp_file, _ = urllib.urlretrieve(self.output.reference)
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


class UnauthorizedException(ServiceException):
    pass


# TODO: Add credentials and tokens
# TODO: Log requests if not already done by owslib (then expose)
# TODO: Support passing ComplexInput's data using POST.
class BirdyClient(object):
    """Returns a class where every public method is a WPS process available at
    the given url.

    Example:
        >>> emu = BirdyClient(url='<server url>')
        >>> emu.hello('stranger')
        'Hello stranger'
    """

    def __init__(
        self,
        url,
        processes=None,
        convert_objects=True,
        converters=None,
        username=None,
        password=None,
        headers=None,
        verify=True,
        cert=None,
        verbose=False,
        version=WPS_DEFAULT_VERSION,
    ):
        """
        Args:
            url (str): Link to WPS provider. config (Config): an instance
            processes: Specify a subset of processes to bind. Defaults to all
                processes.
            convert_objects: If True, object_converters will be used.
            converters (dict): Correspondence of {mimetype: class} to convert
                this mimetype to a python object.
            username (str): passed to :class:`owslib.wps.WebProcessingService`
            password (str): passed to :class:`owslib.wps.WebProcessingService`
            headers (str): passed to :class:`owslib.wps.WebProcessingService`
            verify (bool): passed to :class:`owslib.wps.WebProcessingService`
            cert (str): passed to :class:`owslib.wps.WebProcessingService`
            verbose (str): passed to :class:`owslib.wps.WebProcessingService`
            version (str): WPS version to use.
        """
        self._url = url
        self._convert_objects = convert_objects
        self._converters = converters or copy(default_converters)
        self._username = username
        self._password = password
        self._headers = headers
        self._verify = verify
        self._cert = cert
        self._verbose = verbose
        self._version = version

        self._inputs = {}
        self._outputs = {}

        self._wps = WebProcessingService(
            url,
            version=version,
            username=username,
            password=password,
            verbose=verbose,
            headers=headers,
            verify=verify,
            cert=cert,
            skip_caps=True,
        )

        try:
            self._wps.getcapabilities()
        except ServiceException as e:
            if "AccessForbidden" in str(e):
                raise UnauthorizedException(
                    "You are not authorized to do a request of type: GetCapabilities"
                )

        all_processes = set([p.identifier for p in self._wps.processes])
        if processes is None:
            processes = all_processes
        elif isinstance(processes, six.string_types):
            processes = [processes]

        processes = set([p.lower() for p in processes])

        self._processes = OrderedDict(
            (p.identifier, p)
            for p in self._wps.processes
            if p.identifier.lower() in processes
        )

        if processes - all_processes:
            missing_processes = ", ".join(processes - all_processes)
            raise ValueError(
                "These processes aren't on the WPS: {}".format(missing_processes)
            )

        for pid in self._processes:
            setattr(self, pid, types.MethodType(self._method_factory(pid), self))

    def _method_factory(self, pid):
        """Create a custom function signature with docstring, instantiate it and
        pass it to a wrapper which will actually call the process.

        Args:
            pid: Identifier of the WPS process
        """
        try:
            self._processes[pid] = self._wps.describeprocess(pid)
        except ServiceException as e:
            if "AccessForbidden" in str(e):
                raise UnauthorizedException(
                    "You are not authorized to do a request of type: DescribeProcess"
                )

        process = self._processes[pid]

        input_defaults = OrderedDict(
            (i.identifier, getattr(i, "defaultValue", None)) for i in process.dataInputs
        )

        cleaned_locals = "{k: v for k, v in locals().items() if k not in %s}"
        cleaned_locals = cleaned_locals % str(["self"])

        func_builder = FunctionBuilder(
            name=pid,
            doc=build_doc(process),
            args=["self"] + list(input_defaults),
            defaults=tuple(input_defaults.values()),
            body="return self._execute('{}', **{})".format(pid, cleaned_locals),
            filename=__file__,
            module=self.__module__,
        )

        self._inputs[pid] = {}
        if hasattr(process, "dataInputs"):
            self._inputs[pid] = OrderedDict(
                (i.identifier, i) for i in process.dataInputs
            )

        self._outputs[pid] = {}
        if hasattr(process, "processOutputs"):
            self._outputs[pid] = OrderedDict(
                (o.identifier, o) for o in process.processOutputs
            )

        func = func_builder.get_func()

        return func

    def _execute(self, pid, **kwargs):

        wps_inputs = []
        for name, input_param in self._inputs[pid].items():
            value = kwargs.get(name)
            if value is not None:
                wps_inputs.append((name, convert_input_param(input_param, value)))

        wps_outputs = [
            (o.identifier, "ComplexData" in o.dataType)
            for o in self._outputs[pid].values()
        ]

        # Execute request in synchronous mode
        try:
            resp = self._wps.execute(
                pid, inputs=wps_inputs, output=wps_outputs, mode=SYNC
            )
        except ServiceException as e:
            if "AccessForbidden" in str(e):
                raise UnauthorizedException(
                    "You are not authorized to do a request of type: Execute"
                )

        # Output type conversion
        outputs = [self._process_output(o, pid) for o in resp.processOutputs]
        value = delist(outputs)

        return value

    def _process_output(self, output, pid):
        """Process the output response, whether it is actual data or a URL to a
        file.

        Args:
            output (owslib.wps.Output):
        """
        # Get the data for recognized types.
        if output.data:
            data_type = output.dataType
            if data_type is None:
                data_type = self._outputs[pid][output.identifier].dataType
            data = [convert_output_param(d, data_type) for d in output.data]
            return delist(data)

        if self._convert_objects:
            # Try to convert the bytes to an object.
            converter = self._converters[output.mimeType](output)

            # Convert raw response to python object.
            # The default converter can be modified by users modifying
            # the `default` property of the converter class
            # ex: ShpConverter().default = "fiona"
            return converter.convert()

        else:
            return output.reference


def build_doc(process):
    doc = [process.abstract, ""]

    # Inputs
    if process.dataInputs:
        doc.append("Parameters")
        doc.append("----------")
        for i in process.dataInputs:
            doc.append("{} : {}".format(i.identifier, format_type(i)))
            doc.append("    {}".format(i.abstract or i.title))
            # if i.metadata:
            #    doc[-1] += " ({})".format(', '.join(['`{} <{}>`_'.format(m.title, m.href) for m in i.metadata]))
        doc.append("")

    # Outputs
    if process.processOutputs:
        doc.append("Returns")
        doc.append("-------")
        for i in process.processOutputs:
            doc.append("{} : {}".format(i.identifier, format_type(i)))
            doc.append("    {}".format(i.abstract or i.title))

    doc.append("")
    return "\n".join(doc)


def format_type(obj):
    nmax = 10

    doc = ""
    try:
        if hasattr(obj, "allowedValues"):
            av = ", ".join(["'{}'".format(i) for i in obj.allowedValues[:nmax]])
            if len(obj.allowedValues) > nmax:
                av += ", ..."
            doc += "{" + av + "}"

        if hasattr(obj, "dataType"):
            doc += obj.dataType

        if hasattr(obj, "supportedValues"):
            doc += ", ".join([":mimetype:`{}`".format(f) for f in obj.supportedValues])

        if hasattr(obj, "crss"):
            crss = ", ".join(obj.crss[:nmax])
            if len(obj.crss) > nmax:
                crss += ", ..."
            doc += "[" + crss + "]"

        if hasattr(obj, "minOccurs") and obj.minOccurs == 0:
            doc += ", optional"

        if hasattr(obj, "default"):
            doc += ", default:{0}".format(obj.defaultValue)

        if hasattr(obj, "uoms"):
            doc += ", units:[{}]".format(", ".join([u.uom for u in obj.uoms]))

    except Exception as e:
        raise type(e)("{0} (in {1} docstring)".format(e, obj.identifier))
    return doc


def convert_input_param(param, value):
    # owslib only accepts literaldata, complexdata and boundingboxdata
    if param.dataType:
        if param.dataType == "ComplexData":
            return ComplexDataInput(value)
        if param.dataType == "BoundingBoxData":
            # todo: boundingbox
            return value
    return str(value)


def convert_output_param(value, data_type):
    if "string" in data_type:
        pass
    elif "integer" in data_type:
        value = int(value)
    elif "float" in data_type:
        value = float(value)
    elif "boolean" in data_type:
        value = bool(value)
    elif "dateTime" in data_type:
        value = dateutil.parser.parse(value)
    elif "time" in data_type:
        value = dateutil.parser.parse(value).time()
    elif "date" in data_type:
        value = dateutil.parser.parse(value).date()
    elif "ComplexData" in data_type:
        value = ComplexDataInput(value)
    elif "BoundingBoxData" in data_type:
        # todo: boundingbox
        pass
    return value


# backward compatibility
import_wps = BirdyClient
