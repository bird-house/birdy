# noqa: D100

import tempfile
from collections import namedtuple

import owslib
from owslib.wps import WPSExecution, Output

from birdy.client import utils
from birdy.client.converters import convert
from birdy.exceptions import ProcessFailed, ProcessIsNotComplete
from birdy.utils import delist, sanitize
from .converters import find_converter


class BirdyOutput(Output):
    """An owslib WPS output with user-friendly interface, including conversion methods."""

    def __init__(self, output, path=None, converters=None):
        # Copy owslib.wps.Output attributes
        for key in ["abstract", "title", "identifier", "reference", "dataType"]:
            setattr(self, key, getattr(output, key))
        self.path = path

        # List of converters
        self.converters = find_converter(output, converters)

        if len(self.converters) > 0:
            # Primary converter instance
            self.converter = self.converters[0](output, path=path, verify=False)

            # Copy converter attributes, including `load` method
            for key in ["data", "file", "path", "load"]:
                setattr(self, key, getattr(self.converter, key))


class WPSResult(WPSExecution):  # noqa: D101
    def attach(self, wps_outputs, converters=None):
        """Attach the outputs according to converters.

        Parameters
        ----------
        wps_outputs: dict
        converters: dict
          Converter dictionary {name: object}
        """
        self._wps_outputs = wps_outputs
        self._converters = converters
        self._path = tempfile.mkdtemp()

    def _output_namedtuple(self):
        """Return namedtuple for outputs."""
        Output = namedtuple(
            sanitize(self.process.identifier) + "Response",
            [sanitize(o.identifier) for o in self.processOutputs],
        )
        Output.__repr__ = utils.pretty_repr
        return Output

    def _create_birdy_outputs(self):
        Output = self._output_namedtuple()
        return Output(
            *[BirdyOutput(o) for o in self.processOutputs]
        )

    def load(self):
        """Return BirdyOutput instances.

        TODO: Decide on function name.
        """
        if not self.isComplete():
            raise ProcessIsNotComplete("Please wait ...")
        if not self.isSucceded():
            # TODO: add reason for failure
            raise ProcessFailed("Sorry, process failed.")
        return self._create_birdy_outputs()

    def get(self, asobj=False):
        """Return the process response outputs.

        Parameters
        ----------
        asobj: bool
          If True, object_converters will be used.
        """
        if not self.isComplete():
            raise ProcessIsNotComplete("Please wait ...")
        if not self.isSucceded():
            # TODO: add reason for failure
            raise ProcessFailed("Sorry, process failed.")
        return self._make_output(asobj)

    def _make_output(self, convert_objects=False):
        Output = self._output_namedtuple()
        return Output(
            *[self._process_output(o, convert_objects) for o in self.processOutputs]
        )

    def _process_output(self, output, convert_objects=False):
        """Process the output response, whether it is actual data or a URL to a file.

        Parameters
        ----------
        output: owslib.wps.Output
        convert_objects: bool
          If True, object_converters will be used.
        """
        # Get the data for recognized types.
        if output.data:
            data_type = output.dataType
            if data_type is None:
                data_type = self._wps_outputs[output.identifier].dataType
            data = [utils.from_owslib(d, data_type) for d in output.data]
            return delist(data)

        if convert_objects:
            return convert(output, self._path, self._converters, self.auth.verify)
        else:
            return output.reference
