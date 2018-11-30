from copy import copy
from collections import namedtuple

from birdy.utils import sanitize, delist
from birdy.client import utils
from birdy.client.converters import default_converters
from birdy.exceptions import ProcessIsNotComplete, ProcessFailed


class WPSResult(object):
    def __init__(self, wps_response, wps_outputs, converters=None):
        """
        Args:
            converters (dict): Correspondence of {mimetype: class} to convert
                this mimetype to a python object.
        """
        self._wps_response = wps_response
        self._wps_outputs = wps_outputs
        self._converters = converters or copy(default_converters)

    def get_output(self, convert_objects=False):
        """
        Args:
            convert_objects: If True, object_converters will be used.
        """
        if not self._wps_response:
            raise ValueError("WPS response is not defined.")
        if not self._wps_response.isComplete():
            raise ProcessIsNotComplete("Please wait ...")
        if not self._wps_response.isSucceded():
            # TODO: add reason for failure
            raise ProcessFailed("Sorry, process failed.")
        return self._make_output(convert_objects)

    def _make_output(self, convert_objects=False):
        Output = namedtuple('Output', [sanitize(o.identifier) for o in self._wps_response.processOutputs])
        Output.__repr__ = utils.pretty_repr
        return Output(*[self._process_output(o, convert_objects) for o in self._wps_response.processOutputs])

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
            converter = self._converters[output.mimeType](output)

            # Convert raw response to python object.
            # The default converter can be modified by users modifying
            # the `default` property of the converter class
            # ex: ShpConverter().default = "fiona"
            return converter.convert()

        else:
            return output.reference
