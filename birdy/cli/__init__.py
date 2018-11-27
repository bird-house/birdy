"""
Birdy has a command line interface to interact with a Web Processing Service.

Example
-------
Here is an example with Emu_ WPS service::

    $ birdy -h
    $ birdy hello -h
    $ birdy hello --name stranger
    'Hello Stranger'

Configure WPS service URL
-------------------------
By default Birdy talks to a WPS service on URL http://localhost:5000/wps.
You can change this URL by setting the enivronment variable ``WPS_SERVICE``::

    $ export WPS_SERVICE=http://localhost:5000/wps

Configure SSL verification for HTTPS
------------------------------------
In case you have a WPS serive using HTTPS with a self-signed certificate you need to configure
the environment variable ``WPS_SSL_VERIFY``::

  # deactivate SSL server validation for a self-signed certificate.
  $ export WPS_SSL_VERIFY=false

You can also set the path of the service certificate.
Read the requests_ documentation.

.. _requests: http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
"""
