import types
from collections import OrderedDict
from copy import copy

import six
from boltons.funcutils import FunctionBuilder
from owslib.util import ServiceException
from owslib.wps import WPS_DEFAULT_VERSION, WebProcessingService, SYNC

from birdy.exceptions import UnauthorizedException
from birdy.native import utils
from birdy.native.converters import default_converters


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
        convert_objects=False,
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
        self._convert_objects = convert_objects
        self._converters = converters or copy(default_converters)

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

        wps_processes = OrderedDict((p.identifier, p) for p in self._wps.processes)

        if processes is None:
            processes = list(wps_processes)
        elif isinstance(processes, six.string_types):
            processes = [processes]

        process_names, missing = utils.filter_case_insensitive(
            processes, list(wps_processes)
        )

        if missing:
            message = "These process names are not on the WPS server: {}"
            raise ValueError(message.format(", ".join(missing)))

        self._processes = OrderedDict(
            (name, wps_processes[name]) for name in process_names
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
            doc=utils.build_doc(process),
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
                wps_inputs.append((name, utils.convert_input_value(input_param, value)))

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
        value = utils.delist(outputs)

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
            data = [utils.convert_output_value(d, data_type) for d in output.data]
            return utils.delist(data)

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


# backward compatibility
import_wps = BirdyClient
