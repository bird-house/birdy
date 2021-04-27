# noqa: D100

import tempfile
from collections import namedtuple

from owslib.wps import WPSExecution

from birdy.client import utils
from birdy.client.converters import convert
from birdy.exceptions import ProcessFailed, ProcessIsNotComplete
from birdy.utils import delist, sanitize


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
        Output = namedtuple(
            sanitize(self.process.identifier) + "Response",
            [sanitize(o.identifier) for o in self.processOutputs],
        )
        Output.__repr__ = utils.pretty_repr
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
