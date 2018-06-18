"""
Native Python client for WPS Processes
======================================

The :func:`native_client` function *imports* on the fly a python module whose
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

  >>> from birdy import native_client
  >>> emu = native_client('http://localhost:5000/')
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
import wrapt
from funcsigs import signature  # Py2 Py3 would be from inspect import signature
from collections import OrderedDict
from owslib.wps import ComplexDataInput
from birdy.cli.base import BirdyCLI
from owslib.wps import WebProcessingService
import six


# TODO: Add credentials and tokens
class Config:
    """Configuration class for the BirdMod class and the module it generates. It is designed to
    be used dynamically to modify the behavior of the module before or after its generation.

    Parameters
    ----------
    asobject : bool
      Whether output responses should be dynamically retrieved and converted to Python objects.
      If False the output for ComplexOutput objects will be a link to the output file.
    convert : {str, class}
      A dictionary keyed by mimetype storing the conversion class.

    """
    def __init__(self, asobject=False):
        self._asobject = asobject
        self._convert = {'text/plain': TextConverter,
                         'application/x-netcdf': Netcdf4Converter,
                         'application/json': JSONConverter,
                         'application/geojson': GeoJSONConverter,
                         #'application/x-zipped-shp': ShpConverter,
                         }

    @property
    def asobject(self):
        """Whether or not a file output will be returned as an object
        or a URL string."""
        return self._asobject

    @asobject.setter
    def asobject(self, value):
        assert type(value) == bool
        self._asobject = value

    @property
    def convert(self):
        """Dictionary of conversion classes."""
        return self._convert


class TextConverter:
    mimetype = 'text/plain'
    _default = 'str'

    def __init__(self, output=None):
        """Instantiate the conversion class.

        Parameters
        ----------
        output : owslib.wps.Output
          Output object to be converted.
        """
        self.obj = output

    @property
    def default(self):
        """Default conversion function."""
        return self._default

    @default.setter
    def default(self, value):
        try:
            getattr(self, value)

        except AttributeError:
            raise Exception("This instance has no converter for {}.".format(value))

        except ImportError as e:
            print("{} converter has unmet dependencies: {}".format(value))
            raise e

        self._default = value

    def check(self):
        assert True

    def __call__(self, data=None):
        """Do the conversion from text or bytes to python object."""
        # Get default converter
        c = getattr(self, self.default)

        if data is None:
            data = self.obj.retrieveData()

        # Launch conversion
        return c(data)

    @property
    def str(self):
        return str


class JSONConverter(TextConverter):
    mimetype = 'application/json'
    _default = 'json'

    @property
    def json(self):
        import json
        return json.loads


class GeoJSONConverter(TextConverter):
    mimetype = 'application/geojson'
    _default = 'geojson'

    @property
    def geojson(self):
        import geojson
        return geojson.loads


class Netcdf4Converter(TextConverter):
    mimetype = 'application/x-netcdf'
    _default = 'netcdf4'

    def check(self):
        import netCDF4
        assert netCDF4.getlibversion() > '4.5'

    @property
    def netcdf4(self):
        import netCDF4
        return lambda x: netCDF4.Dataset(self.obj.fileName, memory=x)


class ShpConverter(TextConverter):
    mimetype = 'application/x-zipped-shp'
    _default = 'fiona'

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


# TODO: Deal with authorizations
def native_client(url, name=None, processes=None, **kwds):
    """Return a module with functions calling the WPS processes
     available at the given url.

    Parameters
    ----------
    url : str
      Link to WPS provider.
    name : None
      Module name. Overrides WPS identification is provided.
    processes : None
      Name or list of process names to fetch. If None, all processes will be imported.
    asobject : False
      If True, the client will download the output reference url and try to
      convert it to a know python object. If the mime type is unknown, bytes
      in a string will be returned.


    Returns
    -------
    out : module
      A module where WPS processes can be called using normal python functions.


    Example
    -------
    >>> emu = native_client('<server url>')
    >>> emu.hello('stranger')
    'Hello stranger'

    Notes
    -----
    Use the `_config` attribute to modify the behavior of the module after it has been generated::
    >>> emu._config.asobject = True

    """
    config = Config(**kwds)
    bm = BirdyMod(url=url, config=config)

    # Create module with name from WPS identification.
    mod = types.ModuleType(name or bm.wps.identification.title.split()[0].lower(), bm.wps.identification.abstract)

    # Tie the module configuration to the function builder.
    mod._config = config

    if processes is None:
        processes = bm.processes.keys()

    else:
        if type(processes) in six.string_types:
            processes = [processes, ]
        for p in processes:
            assert p in bm.processes.keys()

    # Generate module functions based on `describeProcess` response.
    for p in processes:
        mod.__dict__[p] = bm.build_function(p)

    return mod


class BirdyMod:
    """
    Construct functions out of WPS processes so they behave as native python functions.
    """
    def __init__(self, url=None, xml=None, config=Config()):

        self.url = os.environ.get('WPS_SERVICE') or url
        self.xml = xml
        self.wps = WebProcessingService(self.url, verify=True, skip_caps=True)
        self.config = config

        # This is a first superficial description of the processes provided by getcapabilities.
        # The full description is fetched with `build_function` using the describeprocess call.
        self.wps.getcapabilities()
        self.processes = OrderedDict()
        for p in self.wps.processes:
            self.processes[p.identifier] = p

        # Store the process description returned by wps.describeprocess.
        self.inputs = {}
        self.outputs = {}

    def build_module(self):
        """Yield the sequence of functions representing WPS processes. """
        for process in self.wps.processes:
            yield process.identifier, self.build_function(process.identifier)

    def build_function(self, pid):
        """Create a custom function signature with docstring, instantiate it
        and pass it to a wrapper which will actually call the process."""

        # Get the process metadata.
        self.processes[pid] = proc = self.wps.describeprocess(pid)
        self.inputs[pid] = OrderedDict()
        self.outputs[pid] = OrderedDict()

        # Create a dummy signature and docstring for the function.
        sig = self.build_function_sig(proc)
        doc = self.build_doc(proc)

        # Create function in the local scope and assign docstring.
        exec(sig)
        f = locals()[pid]
        f.__doc__ = doc

        # Decorate, note that it's the decorator who's calling `execute`.
        return self.decorate()(f)

    def decorate(self):
        """Decorator calling the WPS, using the arguments passed to the wrapped function.
        The wrapped function is a dummy used only for its signature and docstring.

        The wrapt.decorator is used to retain the dummy function name and docstring.
        """

        @wrapt.decorator
        def wrapper(wrapped, instance, args, kwds):
            """Bind the function's arguments to the signature and execute the request.

            Parameters
            ----------
            wrapped : function
              Dummy function whose signature is used to map positional arguments to input identifiers.
            instance : object
              None in this case. This is required by the wrapt.decorator.


            Notes
            -----
            Positional and keyword arguments are all mapped to keyword arguments according
            to the dummy function's signature. These keyword arguments are then passed to
            `execute`.
            """
            sig = signature(wrapped)
            ba = sig.bind(*args, **kwds)
            out = self.execute(wrapped.__name__, **ba.arguments)
            return out

        return wrapper

    def execute(self, identifier, **kwds):
        """Sends an execute request to the WPS server.

        Parameters
        ----------
        identifier : str
          Process identifier.

        kwds : {}
          Process input dictionary, keyed by input identifier. Type conversion,
          for example to `ComplexDataInput` is done within this method.

        Notes
        -----

        """
        from owslib.wps import SYNC

        inputs = []
        for key, values in kwds.items():
            inp = self.inputs[identifier][key]

            # Input type conversion
            typ = BirdyCLI.get_param_type(inp)
            if values is not None:
                values = typ.convert(values, key, None)

            if isinstance(values, ComplexDataInput):
                inputs.append(("{}".format(key), values))
            else:
                inputs.append(("{}".format(key), "{}".format(values)))

        outputs = self.build_output(self.processes[identifier])

        # Execute request in synchronous mode
        resp = self.wps.execute(identifier=identifier, inputs=inputs, output=outputs, mode=SYNC)

        # Output type conversion
        out = []
        for o in resp.processOutputs:
            out.append(self.process_output(o))

        return self.delist(out)

    @staticmethod
    def delist(val):
        """Return list item if list contains only one element."""
        if type(val) == list and len(val) == 1:
            return val[0]
        else:
            return val

    def process_output(self, out):
        """Process the output response, whether it is actual data or a URL to a file."""

        # Get the data for recognized types.
        if out.data:
            typ = BirdyCLI.get_param_type(out)
            data = [typ.convert(d, out.identifier, None) for d in out.data]
            return self.delist(data)

        # Try to convert the bytes to an object.
        if self.config.asobject:
            # Instantiate converter with response output
            converter = self.config.convert[out.mimeType](out)

            # Retrieve data from server. This is a string storing text or bytes.
            data = out.retrieveData()

            # Convert raw response to python object.
            # The default converter can be modified by users using
            # config.convert[<mimetype>].default = new_default.
            return converter(data)

        # Return the URL.
        else:
            return out.reference

    def build_function_sig(self, process):
        """Return the process function signature."""

        template = "\ndef {}({}):\n    pass"

        args, kwds = self.get_args(process)

        return template.format(
            process.identifier,
            ', '.join(args + ['{}={}'.format(k, repr(v)) for k, v in kwds.items()]))

    def get_args(self, process):
        """Return a list of positional arguments and a dictionary of optional keyword arguments
        with their default values."""

        args = []
        kwds = OrderedDict()
        for inp in process.dataInputs:

            # Store for future reference. See `execute`.
            self.inputs[process.identifier][inp.identifier] = inp

            default = BirdyCLI.get_param_default(inp)
            if default is None:
                args.append(inp.identifier)
            else:
                kwds[inp.identifier] = default

        for output in process.processOutputs:
            # Store for future reference. See `execute`.

            self.outputs[process.identifier][output.identifier] = output

        return args, kwds

    def build_output(self, process):
        """Return output list."""
        return [(k, v.dataType == 'ComplexData') for k, v in self.outputs[process.identifier].items()]

    def build_doc(self, process):
        """Return function docstring built from WPS metadata."""

        doc = list([3 * '\"'])
        doc.append(process.abstract)
        doc.append('')

        # Inputs
        if process.dataInputs:
            doc.append('Parameters')
            doc.append('----------')
            for i in process.dataInputs:
                doc.append("{} : {}".format(i.identifier, self.fmt_type(i)))
                doc.append("    {}".format(i.abstract or i.title))
                # if i.metadata:
                #    doc[-1] += " ({})".format(', '.join(['`{} <{}>`_'.format(m.title, m.href) for m in i.metadata]))
            doc.append('')

        # Outputs
        if process.processOutputs:
            doc.append("Returns")
            doc.append("-------")
            for i in process.processOutputs:
                doc.append("{} : {}".format(i.identifier, self.fmt_type(i)))
                doc.append("    {}".format(i.abstract or i.title))

        doc.extend(['', ''])
        doc.append(3 * '\"')
        return '\n'.join(doc)

    @staticmethod
    def fmt_type(obj):
        """Input and output type formatting (type, default and allowed
        values).
        """
        nmax = 10

        doc = ''
        try:
            if getattr(obj, 'allowedValues', None):
                av = ', '.join(["'{}'".format(i) for i in obj.allowedValues[:nmax]])
                if len(obj.allowedValues) > nmax:
                    av += ', ...'

                doc += "{" + av + "}"

            elif getattr(obj, 'dataType', None):
                doc += obj.dataType

            elif getattr(obj, 'supportedValues', None):
                doc += ', '.join([':mimetype:`{}`'.format(f.mimeType) for f in obj.supportedValues])

            elif getattr(obj, 'crss', None):
                doc += "[" + ', '.join(obj.crss[:nmax])
                if len(obj.crss) > nmax:
                    doc += ', ...'
                doc += "]"

            if getattr(obj, 'minOccurs', None) is not None:
                if obj.minOccurs == 0:
                    doc += ', optional'
                    if getattr(obj, 'default', None):
                        doc += ', default:{0}'.format(obj.defaultValue)

            if getattr(obj, 'uoms', None):
                doc += ', units:[{}]'.format(', '.join([u.uom for u in obj.uoms]))

        except Exception as e:
            raise type(e)(e.message + ' in {0} docstring'.format(obj.identifier))
        return doc
