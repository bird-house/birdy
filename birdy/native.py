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
from copy import copy

import click
import six
import types
from importlib import import_module
from collections import OrderedDict

from owslib.util import ServiceException
from owslib.wps import WPS_DEFAULT_VERSION, SYNC
from owslib.wps import WebProcessingService
from boltons.funcutils import FunctionBuilder

from birdy.cli.base import BirdyCLI
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

    __call__ = convert

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

        if getlibversion() < "4.5":
            raise ImportError("netCDF4 library must be at least version 4.5")

    def convert_data(self, data):
        """
        Args:
            data:
        """
        import netCDF4

        return netCDF4.Dataset(self.output.fileName, memory=data)


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
    # todo: identify when unauthorized
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

        Returns:
            _WPSWrapper: A class containing WPS processes as methods.

        Notes:
            Use the `config` attribute to modify the behavior of the class after
            it has been generated: >>> emu.config.asobject = True
        """

        self._url = url
        self._processes_filter = processes
        self._convert_objects = convert_objects
        self._converters = converters or copy(default_converters)
        self._username = username
        self._password = password
        self._headers = headers
        self._verify = verify
        self._cert = cert
        self._verbose = verbose
        self._version = version

        self.wps = WebProcessingService(
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
            self.wps.getcapabilities()
        except UnauthorizedException:
            raise

        list_filter = (
            self._processes_filter
            if not isinstance(self._processes_filter, six.string_types)
            else [self._processes_filter]
        )

        self._processes = OrderedDict(
            (p.identifier, p)
            for p in self.wps.processes
            if list_filter is None or p.identifier in list_filter
        )

        self._inputs = {}
        self._outputs = {}

        for pid in self._processes:
            setattr(self, pid, types.MethodType(self._method_factory(pid), self))

    def _method_factory(self, pid):
        """Create a custom function signature with docstring, instantiate it and
        pass it to a wrapper which will actually call the process.

        Args:
            pid: Identifier of the WPS process
        """
        try:
            self._processes[pid] = self.wps.describeprocess(pid)
        except UnauthorizedException:
            raise

        process = self._processes[pid]

        input_defaults = {
            i.identifier: BirdyCLI.get_param_default(i) for i in process.dataInputs
        }

        cleaned_locals = "{k: v for k, v in locals().items() if k not in %s}"
        cleaned_locals = cleaned_locals % str(["self"])

        func_builder = FunctionBuilder(
            name=pid,
            doc=self.build_doc(process),
            args=["self"] + list(input_defaults),
            defaults=tuple(input_defaults.values()),
            body="return self.execute('{}', **{})".format(pid, cleaned_locals),
            filename=__file__,
            module=self.__module__,
        )

        self._inputs[pid] = {}
        if hasattr(process, "dataInputs"):
            self._inputs[pid] = OrderedDict(
                (p.identifier, p) for p in process.dataInputs
            )

        self._outputs[pid] = {}
        if hasattr(process, "dataOutputs"):
            self.outputs[pid] = OrderedDict(
                (p.identifier, p) for p in process.dataOutputs
            )

        func = func_builder.get_func()

        return func

    def execute(self, pid, **kwargs):
        """
        Args:
            pid:
            **kwargs:
        """
        execute_inputs = {k: v for k, v in kwargs.items() if k in self._inputs[pid]}

        def is_complex_input(input_):
            return "ComplexData" in input_.dataType

        wps_inputs = [
            (k, convert_input_param(self._inputs[pid][k], v))
            for k, v in execute_inputs.items()
        ]
        wps_outputs = [(o.identifier, is_complex_input(o)) for o in self._outputs[pid]]

        # Execute request in synchronous mode
        try:
            resp = self.wps.execute(
                pid, inputs=wps_inputs, output=wps_outputs, mode=SYNC
            )
        except UnauthorizedException:
            raise

        # Output type conversion
        outputs = [self._process_output(o) for o in resp.processOutputs]
        value = delist(outputs)

        return value

    def _process_output(self, output):
        """Process the output response, whether it is actual data or a URL to a
        file.

        Args:
            output (owslib.wps.Output):
        """

        # Get the data for recognized types.
        if output.data:
            data = [convert_output_param(output, d) for d in output.data]
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

    def build_doc(self, process):
        """Return function docstring built from WPS metadata.

        Args:
            process:
        """

        doc = [process.abstract, ""]

        # Inputs
        if process.dataInputs:
            doc.append("Parameters")
            doc.append("----------")
            for i in process.dataInputs:
                doc.append("{} : {}".format(i.identifier, self.fmt_type(i)))
                doc.append("    {}".format(i.abstract or i.title))
                # if i.metadata:
                #    doc[-1] += " ({})".format(', '.join(['`{} <{}>`_'.format(m.title, m.href) for m in i.metadata]))
            doc.append("")

        # Outputs
        if process.processOutputs:
            doc.append("Returns")
            doc.append("-------")
            for i in process.processOutputs:
                doc.append("{} : {}".format(i.identifier, self.fmt_type(i)))
                doc.append("    {}".format(i.abstract or i.title))

        doc.append("")
        return "\n".join(doc)

    @staticmethod
    def fmt_type(obj):
        """Input and output type formatting (type, default and allowed values).

        Args:
            obj:
        """
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
                doc += ", ".join(
                    [":mimetype:`{}`".format(f) for f in obj.supportedValues]
                )

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
    """
    Args:
        param:
        value:
    """
    type_ = BirdyCLI.get_param_type(param)
    # owslib only accepts literaldata, complexdata and boundingboxdata
    # todo: boundingbox
    if type_ in [click.INT, click.BOOL, click.FLOAT]:
        type_ = click.STRING
        value = str(value)
    return type_.convert(value, param=None, ctx=None)


def convert_output_param(param, value):
    """
    Args:
        param:
        value:
    """
    type_ = BirdyCLI.get_param_type(param)
    return type_.convert(value, param=None, ctx=None)


# backward compatibility
import_wps = BirdyClient
