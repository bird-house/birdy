"""
The :class:`WPSClient` class aims to make working with WPS servers easy,
even without any prior knowledge of WPS.

Calling the :class:`WPSClient` class creates an instance whose methods call
WPS processes. These methods are generated at runtime based on the
process description provided by the WPS server. Calling a function sends
an `execute` request to the server. The server response is parsed and
returned as a :class:`WPSExecution` instance, which includes information
about the job status, the progress percentage, the starting time, etc. The
actual output from the process are obtained by calling the `get` method.

The output is parsed to convert the outputs in native Python whenever possible.
`LiteralOutput` objects (string, float, integer, boolean) are automatically
converted to their native format. For `ComplexOutput`, the module can either
return a link to the output files stored on the server, or try to
convert the outputs to a Python object based on their mime type. This conversion
will occur with `get(asobj=True)`. So for example, if the mime type is
'application/json', the output would be a `dict`.

Inputs to processes can be native Python types (string, float, int, date, datetime),
http links or local files. Local files can be transferred to a remote server by
including their content into the WPS request. Simply set the input to a valid path
or file object and the client will take care of reading and converting the file.


Example
-------
If a WPS server with a simple `hello` process is running on the local host on port 5000::

  >>> from birdy import WPSClient
  >>> emu = WPSClient('http://localhost:5000/')
  >>> emu.hello
  <bound method hello of <birdy.client.base.WPSClient object>>
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

  # Call the function. The output is a namedtuple
  >>> emu.hello('stranger')
  hello(output='Hello stranger')

"""

from .base import WPSClient, nb_form
