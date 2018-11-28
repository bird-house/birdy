"""
The :class:`WPSClient` instantiates a class whose methods call
WPS processes. The methods are generated at runtime based on the
process description provided by the WPS server. Calling a function sends
an `execute` request to the server, which returns a response.

The response is parsed to convert the outputs in native Python whenever possible.
`LiteralOutput` objects (string, float, integer, boolean) are automatically
converted to their native format. For `ComplexOutput`, the module can either
return a link to the output files stored on the server (default), or try to
convert the outputs to a Python object based on their mime type. So for example,
if the mime type is 'application/json', the module would read the remote output
file and `json.loads` it to return a `dict`.

The behavior of the module can be configured using the :class:`config`, see its
docstring for more information.

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

from .base import WPSClient
