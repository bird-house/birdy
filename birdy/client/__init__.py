# noqa: D205, D400
"""
WPSClient Class
===============

The :class:`WPSClient` class aims to make working with WPS servers easy, even without any prior knowledge of WPS.

Calling the :class:`WPSClient` class creates an instance whose methods call WPS processes.
These methods are generated at runtime based on the process description provided by the WPS server.
Calling a function sends an `execute` request to the server. The server response is parsed and
returned as a :class:`WPSExecution` instance, which includes information about the job status, the progress percentage,
the starting time, etc. The actual output from the process are obtained by calling the `get` method.

The output is parsed to convert the outputs in native Python whenever possible.
`LiteralOutput` objects (string, float, integer, boolean) are automatically converted to their native format.
For `ComplexOutput`, the module can either return a link to the output files stored on the server,
or try to convert the outputs to a Python object based on their mime type. This conversion will occur with
`get(asobj=True)`. So for example, if the mime type is 'application/json', the output would be a `dict`.

Inputs to processes can be native Python types (string, float, int, date, datetime), http links or local files.
Local files can be transferred to a remote server by including their content into the WPS request.
Simply set the input to a valid path or file object and the client will take care of reading and converting the file.

Example
-------
If a WPS server with a simple `hello` process is running on the local host on port 5000::

  >>> from birdy import WPSClient
  >>> emu = WPSClient('http://localhost:5000/')
  >>> emu.hello
  <bound method hello of <birdy.client.base.WPSClient object>>
  >>> print(emu.hello.__doc__)

  # Just says a friendly Hello. Returns a literal string output with Hello plus the inputed name.

  # Parameters
  # ----------
  # name : string
  #     Please enter your name.
  #
  # Returns
  # -------
  # output : string
  #     A friendly Hello from us.
  #
  # ""
  #
  # # Call the function. The output is a namedtuple
  # >>> emu.hello('stranger')
  # hello(output='Hello stranger')

Authentication
--------------
If you want to connect to a server that requires authentication, the :class:`WPSClient` class accepts
an `auth` argument that behaves exactly like in the popular `requests` module (see `requests Authentication`_)

The simplest form of authentication is HTTP Basic Auth. Although
wps processes are not commonly protected by this authentication method,
here is a simple example of how to use it::

    >>> from birdy import WPSClient
    >>> from requests.auth import HTTPBasicAuth
    >>> auth = HTTPBasicAuth('user', 'pass')
    >>> wps = WPSClient('http://www.example.com/wps', auth=auth)

Because any `requests`-compatible class is accepted, custom authentication methods are implemented
the same way as in `requests`.

For example, to connect to a magpie_ protected wps, you can use the requests-magpie_ module::

    >>> from birdy import WPSClient
    >>> from requests_magpie import MagpieAuth
    >>> auth = MagpieAuth('https://www.example.com/magpie', 'user', 'pass')
    >>> wps = WPSClient('http://www.example.com/wps', auth=auth)

Output format
-------------

Birdy automatically manages process output to reflect its default values or Birdy's own defaults.

However, it's possible to customize the output of a process. Each process has an input
named ``output_formats``, that takes a dictionary as a parameter::

    # example format = {
    #     'output_identifier': {
    #         'as_ref': <True, False or None>
    #         'mimetype': <MIME type as a string or None>,
    #     },
    # }

    # A dictionary defining netcdf and json outputs
    >>> custom_format = {
    >>>     'netcdf': {
    >>>         'as_ref': True,
    >>>         'mimetype': 'application/json',
    >>>     },
    >>>     'json': {
    >>>         'as_ref': False,
    >>>         'mimetype': None
    >>>     }
    >>> }

Utility functions can also be used to create this dictionary::

    >>> custom_format = create_output_dictionary('netcdf', True, 'application/json')
    >>> add_output_format(custom_format, 'json', False, None)

The created dictionary can then be used with a process::

    >>> cli = WPSClient("http://localhost:5000")
    >>> z = cli.output_formats(output_formats=custom_format).get()
    >>> z

.. _requests Authentication: https://2.python-requests.org/en/master/user/authentication/
.. _magpie: https://github.com/ouranosinc/magpie
.. _requests-magpie: https://github.com/ouranosinc/requests-magpie
"""

from birdy.client.notebook import gui  # noqa: F401

from .base import WPSClient, nb_form  # noqa: F401
