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
import os
import types
from textwrap import dedent

import wrapt
from funcsigs import signature  # Py2 Py3 would be from inspect import signature
from collections import OrderedDict

form
boltons.funcutils
import FunctionBuilder

from owslib.util import ServiceException
from owslib.wps import ComplexDataInput, WPS_DEFAULT_VERSION, SYNC
from birdy.cli.base import BirdyCLI
from owslib.wps import WebProcessingService
import six


# TODO: Add credentials and tokens
# TODO: Log requests if not already done by owslib (then expose)
# TODO: Support passing ComplexInput's data using POST.
class Config(object):
    """Configuration class for the BirdMod class and the module it generates. It
    is designed to be used dynamically to modify the behavior of the module
    before or after its generation.

    Args:
        asobject (bool): Whether output responses should be dynamically
            retrieved and converted to Python objects. If False the output for
            ComplexOutput objects will be a link to the output file.
        convert ({str, class}): A dictionary keyed by mimetype storing the
            conversion class.
    """

    def __init__(self, asobject=False):
        """
        Args:
            asobject:
        """
        self._asobject = asobject
        self._convert = {
            "text/plain": TextConverter,
            "application/x-netcdf": Netcdf4Converter,
            "application/json": JSONConverter,
            "application/geojson": GeoJSONConverter,
            # 'application/x-zipped-shp': ShpConverter,
        }

    @property
    def asobject(self):
        """Whether or not a file output will be returned as an object or a URL
        string.
        """
        return self._asobject

    @asobject.setter
    def asobject(self, value):
        """
        Args:
            value:
        """
        self._asobject = bool(value)

    @property
    def convert(self):
        """Dictionary of conversion classes."""
        return self._convert


class TextConverter(object):
    mimetype = "text/plain"
    _default = "str"

    def __init__(self, output=None):
        """Instantiate the conversion class.

        Args:
            output (owslib.wps.Output): Output object to be converted.
        """
        self.obj = output
        self.check()

    @property
    def default(self):
        """Default conversion function."""
        return self._default

    @default.setter
    def default(self, value):
        """
        Args:
            value:
        """
        try:
            getattr(self, value)

        except AttributeError:
            raise Exception("This instance has no converter for {}.".format(value))

        except ImportError as e:
            print("{} converter has unmet dependencies: {}".format(value, e))
            raise e

        self._default = value

    @staticmethod
    def check():
        return None


def __call__(self, data=None):
    """Do the conversion from text or bytes to python object.

    Args:
        data:
    """
    # Get default converter
    c = getattr(self, self.default)

    if data is None:
        data = self.obj.retrieveData()

    # Launch conversion
    return c(data)


def str(self, data):
    """
    Args:
        data:
    """
    if isinstance(data, bytes):
        return data.decode("utf-8")
    elif isinstance(data, str):
        return data


class JSONConverter(TextConverter):
    mimetype = "application/json"
    _default = "json"

    @property
    def json(self):
        import json

        return json.loads


class GeoJSONConverter(TextConverter):
    mimetype = "application/geojson"
    _default = "geojson"

    @property
    def geojson(self):
        import geojson

        return geojson.loads


class Netcdf4Converter(TextConverter):
    mimetype = "application/x-netcdf"
    _default = "netcdf4"

    @staticmethod
    def check():
        import netCDF4

        if netCDF4.getlibversion() < "4.5":
            raise NotImplementedError

    @property
    def netcdf4(self):
        import netCDF4

        return lambda x: netCDF4.Dataset(self.obj.fileName, memory=x)


class ShpConverter(TextConverter):
    mimetype = "application/x-zipped-shp"
    _default = "fiona"

    @property
    def fiona(self):
        raise NotImplementedError
        # import fiona
        # import io
        # return lambda x: fiona.open(io.BytesIO(x))

    @property
    def ogr(self):
        raise NotImplementedError
        # from osgeo import ogr
        # return ogr.Open


class UnauthorizedException(ServiceException):
    pass


def import_wps(
        url,
        config=None,
        processes=None,
        version=WPS_DEFAULT_VERSION,
        username=None,
        password=None,
        verbose=False,
        skip_caps=False,
        headers=None,
        verify=True,
        cert=None,
        asobject=False,
):
    """Returns a class with methods calling the WPS processes
        available at the given url.

    Example:
        >>> emu = import_wps('<server url>')
        >>> emu.hello('stranger')
        'Hello stranger'

    Args:
        url (str): Link to WPS provider.
        config (Config): an instance of :class:`Config`. Falls back to the
            default configuration if None.
        processes (bool): Name or list of process names to fetch. By default,
            all processes will be imported.
        version (str): passed to :class:`owslib.wps.WebProcessingService`
        username (str): passed to :class:`owslib.wps.WebProcessingService`
        password (str): passed to :class:`owslib.wps.WebProcessingService`
        verbose (str): passed to :class:`owslib.wps.WebProcessingService`
        headers (str): passed to :class:`owslib.wps.WebProcessingService`
        verify (bool): passed to :class:`owslib.wps.WebProcessingService`
        cert (str): passed to :class:`owslib.wps.WebProcessingService`
        asobject (bool): False If True, the client will download the output
            reference url and try to convert it to a know python object. If the
            mime type is unknown, bytes in a string will be returned.

    Returns:
        _WPSWrapper: A class containing WPS processes as methods.

    Notes:
        Use the `config` attribute to modify the behavior of the class after it
        has been generated: >>> emu.config.asobject = True
    """
    if not isinstance(config, Config):
        config = Config()

    return _WPSWrapper(
        url=url,
        config=config,
        version=version,
        username=username,
        password=password,
        verbose=verbose,
        headers=headers,
        verify=verify,
        cert=cert
    )


class _WPSWrapper(object):
    def __init__(
            self, url, config, version, username, password, verbose, headers, verify, cert
    ):
        self.url = url
        self.config = config
        self.inputs = {}
        self.outputs = {}

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

        self.processes = OrderedDict((p.identifier, p) for p in self.wps.processes)

        for p in self.processes:
            # todo: slug identifier
            pid = p.identifier
            setattr(self, pid, self.method_factory(pid))

    def get_capabilities(self):
        pass  # todo

    # todo: make this private
    def method_factory(self, pid):
        """Create a custom function signature with docstring, instantiate it and
        pass it to a wrapper which will actually call the process.

        Args:
            pid: Idenfifier of the WPS process
        """
        try:
            self.processes[pid] = self.wps.describeprocess(pid)
        except UnauthorizedException:
            raise

        process = self.processes[pid]

        input_defaults = {i.identifier: BirdyCLI.get_param_default(i) for i in process.dataInputs}
        input_names = list(input_defaults)

        # todo: implement describe()
        func = FunctionBuilder(
            name=pid,
            doc=process.abstract,  # todo: make better doc
            args=["self"],
            kwonlyargs=input_names,
            kwonlydefaults=input_defaults,
            body=["self.execute({pid}, locals())".format(pid=pid)],
            filename=__file__,
            module=self.__module__,
        )

        self.inputs[pid] = OrderedDict((i.identifier, i) for i in process.dataInputs)
        self.outputs[pid] = OrderedDict((o.identifier, o) for o in process.dataOutputs)

        return func

    def execute(self, pid, **kwargs):
        execute_inputs = {k: v for k, v in kwargs if k in self.inputs[pid]}

        def convert_func(input_):
            return ComplexDataInput if "ComplexData" in input_.dataType else str

        inputs = [(k: convert_func(k)(v)) for k, v in execute_inputs.items()]

        outputs = [(k, v.dataType == "ComplexData") for k, v in self.outputs[pid].items()]

        # Execute request in synchronous mode
        try:
            resp = self.wps.execute(identifier=pid, inputs=inputs, output=outputs, mode=SYNC)
        except UnauthorizedException:
            raise

        # Output type conversion
        out = [self.process_output(o, pid) for o in resp.processOutputs]
        value = out[0] if len(out) == 1 else out

        return value

    def process_output(self, out, identifier=None):
        """Process the output response, whether it is actual data or a URL to a
        file.

        Args:
            out:
            identifier:
        """

        # todo


    def build_doc(self, process):
        """Return function docstring built from WPS metadata.

        Args:
            process:
        """

        doc = list([3 * '"'])
        doc.append(process.abstract)
        doc.append("")

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

        doc.extend(["", ""])
        doc.append(3 * '"')
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
            if getattr(obj, "allowedValues", None):
                av = ", ".join(["'{}'".format(i) for i in obj.allowedValues[:nmax]])
            if len(obj.allowedValues) > nmax:
                av += ", ..."

                doc += "{" + av + "}"

            elif getattr(obj, "dataType", None):
                doc += obj.dataType

            elif getattr(obj, "supportedValues", None):
                doc += ", ".join(
                    [":mimetype:`{}`".format(f.mimeType) for f in obj.supportedValues]
                )

            elif getattr(obj, "crss", None):
                doc += "[" + ", ".join(obj.crss[:nmax])
            if len(obj.crss) > nmax:
                doc += ", ..."
                doc += "]"

            if getattr(obj, "minOccurs", None) is not None:
                if obj.minOccurs == 0:
                    doc += ", optional"
                    if getattr(obj, "default", None):
                        doc += ", default:{0}".format(obj.defaultValue)

            if getattr(obj, "uoms", None):
                doc += ", units:[{}]".format(", ".join([u.uom for u in obj.uoms]))

        except Exception as e:
            raise type(e)(e.message + " in {0} docstring".format(obj.identifier))
        return doc
