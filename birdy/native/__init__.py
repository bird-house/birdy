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

from .client import BirdyClient, import_wps

