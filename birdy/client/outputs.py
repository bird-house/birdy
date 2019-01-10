from copy import copy
from collections import namedtuple

from birdy.utils import sanitize, delist
from birdy.client import utils
from birdy.client.converters import default_converters
from birdy.exceptions import ProcessIsNotComplete, ProcessFailed
from owslib.wps import WPSExecution
import warnings


class WPSResult(WPSExecution):

    def attach(self, wps_outputs, converters=None):
        """
        Args:
            converters (dict): Correspondence of {mimetype: class} to convert
                this mimetype to a python object.
        """
        self._wps_outputs = wps_outputs
        self._converters = converters or copy(default_converters)

    def get(self, asobj=False):
        """
        Args:
            asobj: If True, object_converters will be used.
        """
        if not self.isComplete():
            raise ProcessIsNotComplete("Please wait ...")
        if not self.isSucceded():
            # TODO: add reason for failure
            raise ProcessFailed("Sorry, process failed.")
        return self._make_output(asobj)

    def _make_output(self, convert_objects=False):
        Output = namedtuple(self.process.identifier + 'Response', [sanitize(o.identifier) for o in self.processOutputs])
        Output.__repr__ = utils.pretty_repr
        return Output(*[self._process_output(o, convert_objects) for o in self.processOutputs])

    def _process_output(self, output, convert_objects=False):
        """Process the output response, whether it is actual data or a URL to a
        file.

        Args:
            output (owslib.wps.Output):
            convert_objects: If True, object_converters will be used.
        """
        # Get the data for recognized types.
        if output.data:
            data_type = output.dataType
            if data_type is None:
                data_type = self._wps_outputs[output.identifier].dataType
            data = [utils.from_owslib(d, data_type) for d in output.data]
            return delist(data)

        if convert_objects and output.mimeType:
            # Try to convert the bytes to an object.
            # The default converter can be modified by users modifying
            # the `default` property of the converter class
            # ex: ShpConverter().default = "fiona"
            if output.mimeType in self._converters:
                converter = self._converters[output.mimeType](output)
                return converter.convert()
            else:
                warnings.warn(UserWarning("No converter was found for mime type: {}".format(output.mimeType)))
                return output.reference
        else:
            return output.reference
