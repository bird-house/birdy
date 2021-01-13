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

Use an OAuth2 access token
--------------------------

If the WPS service is secured by an OAuth2 access tokens
then you can provide an access token with the ``--token`` option::

    $ birdy --token abc123 hello --name stranger

Use client certificate to access WPS service
--------------------------------------------

If the WPS service is secured by x509 certificates you can add a certificate
with the ``--cert`` option to a request::

   # run hello with certificate
   $ birdy --cert cert.pem hello --name stranger

Using the output_formats option for a process
---------------------------------------------

Each process also has a default option named `output_formats`. It can be used
to override a process' output format's default values.

This option takes three parameters;

The format identifier: the name given to it

The ``as reference`` parameter: if the output is returned as a link of not.
Can be True, False, or None (which uses the process' default value)

The MIME type: of which MIME type is the output.
Unless the process has multiple supported mime types, this can be left to None.

Looking at the emu process `output_formats`, the JSON output's default's the ``as reference``
parameter to False and returns the content directly::

    $ birdy output_formats
      Output:
      netcdf=http://localhost:5000/outputs/d9abfdc4-08d6-11eb-9334-0800274cd70c/dummy.nc
      json=['{"testing": [1, 2]}']

We can then use the output_formats option to redefine it::

    $ birdy output_formats --output_formats json True None
      Output:
      netcdf=http://localhost:5000/outputs/38e9aefe-08db-11eb-9334-0800274cd70c/dummy.nc
      json=http://localhost:5000/outputs/38e9aefe-08db-11eb-9334-0800274cd70c/dummy.json

.. _requests: http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
"""
