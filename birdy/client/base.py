import types
from collections import OrderedDict
from textwrap import dedent
from boltons.funcutils import FunctionBuilder

import owslib
from owslib.util import ServiceException
from owslib.wps import WPS_DEFAULT_VERSION, WebProcessingService, SYNC, ASYNC, ComplexData

from birdy.exceptions import UnauthorizedException
from birdy.client import utils
from birdy.utils import sanitize, fix_url, embed
from birdy.client import notebook
from birdy.client.outputs import WPSResult

import logging


# TODO: Support passing ComplexInput's data using POST.
class WPSClient(object):
    """Returns a class where every public method is a WPS process available at
    the given url.

    Example:
        >>> emu = WPSClient(url='<server url>')
        >>> emu.hello('stranger')
        'Hello stranger'
    """

    def __init__(
        self,
        url,
        processes=None,
        converters=None,
        username=None,
        password=None,
        headers=None,
        verify=True,
        cert=None,
        verbose=False,
        progress=False,
        version=WPS_DEFAULT_VERSION,
    ):
        """
        Args:
            url (str): Link to WPS provider. config (Config): an instance
            processes: Specify a subset of processes to bind. Defaults to all
                processes.
            converters (dict): Correspondence of {mimetype: class} to convert
                this mimetype to a python object.
            username (str): passed to :class:`owslib.wps.WebProcessingService`
            password (str): passed to :class:`owslib.wps.WebProcessingService`
            headers (str): passed to :class:`owslib.wps.WebProcessingService`
            verify (bool): passed to :class:`owslib.wps.WebProcessingService`
            cert (str): passed to :class:`owslib.wps.WebProcessingService`
            verbose (str): passed to :class:`owslib.wps.WebProcessingService`
            progress (bool): If True, enable interactive user mode.
            version (str): WPS version to use.
        """
        self._converters = converters
        self._interactive = progress
        self._mode = ASYNC if progress else SYNC
        self._notebook = notebook.is_notebook()
        self._inputs = {}
        self._outputs = {}

        if not verify:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
            raise

        self._processes = self._get_process_description(processes)

        # Build the methods
        for pid in self._processes:
            setattr(self, sanitize(pid), types.MethodType(self._method_factory(pid), self))

        self.logger = logging.getLogger('WPSClient')
        if progress:
            self._setup_logging()

        self.__doc__ = utils.build_wps_client_doc(self._wps, self._processes)

    def _get_process_description(self, processes):
        """Return the description for each process.

        Sends the server a `describeProcess` request for each process.

        Parameters
        ----------
        processes: str, list, None
          A process name, a list of process names or None (for all processes).

        Returns
        -------
        OrderedDict
          A dictionary keyed by the process identifier of process descriptions.
        """
        all_wps_processes = [p.identifier for p in self._wps.processes]

        if processes is None:
            if owslib.__version__ > '0.17.0':
                # Get the description for all processes in one request.
                ps = self._wps.describeprocess('all')
                return OrderedDict((p.identifier, p) for p in ps)
            else:
                processes = all_wps_processes

        # Check for invalid process names, i.e. not matching the getCapabilities response.

        process_names, missing = utils.filter_case_insensitive(
            processes, all_wps_processes)

        if missing:
            message = "These process names were not found on the WPS server: {}"
            raise ValueError(message.format(", ".join(missing)))

        # Get the description for each process.
        ps = [self._wps.describeprocess(pid) for pid in process_names]

        return OrderedDict((p.identifier, p) for p in ps)

    def _setup_logging(self):
        self.logger.setLevel(logging.INFO)
        import sys
        fh = logging.StreamHandler(sys.stdout)
        fh.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        self.logger.addHandler(fh)

    def _method_factory(self, pid):
        """Create a custom function signature with docstring, instantiate it and
        pass it to a wrapper which will actually call the process.

        Parameters
        ----------
        pid: str
          Identifier of the WPS process.

        Returns
        -------
        func
          A Python function calling the remote process, complete with docstring and signature.
        """

        process = self._processes[pid]

        input_defaults = OrderedDict()
        for inpt in process.dataInputs:
            iid = sanitize(inpt.identifier)
            default = getattr(inpt, "defaultValue", None) if inpt.dataType != 'ComplexData' else None
            input_defaults[iid] = utils.from_owslib(default, inpt.dataType)

        body = dedent("""
            inputs = locals()
            inputs.pop('self')
            return self._execute('{pid}', **inputs)
        """).format(pid=pid)

        func_builder = FunctionBuilder(
            name=sanitize(pid),
            doc=utils.build_process_doc(process),
            args=["self"] + list(input_defaults),
            defaults=tuple(input_defaults.values()),
            body=body,
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
        """Execute the process."""
        wps_inputs = []
        for name, input_param in self._inputs[pid].items():
            value = kwargs.get(sanitize(name))
            if value is not None:
                if isinstance(input_param.defaultValue, ComplexData):
                    encoding = input_param.defaultValue.encoding
                    mimetype = input_param.defaultValue.mimeType

                    if isinstance(value, ComplexData):
                        inp = value

                    else:
                        if utils.is_embedded_in_request(self._wps.url, value):
                            # If encoding is None, this will return the actual encoding used (utf-8 or base64).
                            value, encoding = embed(value, mimetype, encoding=encoding)
                        else:
                            value = fix_url(value)

                        inp = utils.to_owslib(value,
                                              data_type=input_param.dataType,
                                              encoding=encoding,
                                              mimetype=mimetype)

                else:
                    inp = utils.to_owslib(value, data_type=input_param.dataType)

                wps_inputs.append((name, inp))

        wps_outputs = [
            (o.identifier, "ComplexData" in o.dataType)
            for o in self._outputs[pid].values()
        ]

        mode = self._mode if self._processes[pid].storeSupported else SYNC

        try:
            wps_response = self._wps.execute(
                pid, inputs=wps_inputs, output=wps_outputs, mode=mode
            )

            if self._interactive and self._processes[pid].statusSupported:
                if self._notebook:
                    notebook.monitor(wps_response, sleep=.2)
                else:
                    self._console_monitor(wps_response)

        except ServiceException as e:
            if "AccessForbidden" in str(e):
                raise UnauthorizedException(
                    "You are not authorized to do a request of type: Execute"
                )
            raise

        # Add the convenience methods of WPSResult to the WPSExecution class. This adds a `get` method.
        utils.extend_instance(wps_response, WPSResult)
        wps_response.attach(wps_outputs=self._outputs[pid], converters=self._converters)
        return wps_response

    def _console_monitor(self, execution, sleep=3):
        """Monitor the execution of a process.

        Parameters
        ----------
        execution : WPSExecution instance
          The execute response to monitor.
        sleep: float
          Number of seconds to wait before each status check.
        """
        import signal

        # Intercept CTRL-C
        def sigint_handler(signum, frame):
            self.cancel()
        signal.signal(signal.SIGINT, sigint_handler)

        while not execution.isComplete():
            execution.checkStatus(sleepSecs=sleep)
            self.logger.info("{} [{}/100] - {} ".format(
                execution.process.identifier,
                execution.percentCompleted,
                execution.statusMessage[:50],))

        if execution.isSucceded():
            self.logger.info("{} done.".format(execution.process.identifier))
        else:
            self.logger.info("{} failed.".format(execution.process.identifier))


def nb_form(wps, pid):
    """Return a Notebook form to enter input values and launch process."""
    if wps._notebook:
        return notebook.interact(
            func=getattr(wps, sanitize(pid)),
            inputs=wps._inputs[pid].items())
    else:
        return None
