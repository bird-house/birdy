.. _usage:

*****
Usage
*****

Using the command line
======================

Get a list of available processes on WPS with URL http://localhost:5000/wps:

.. code-block:: sh

   # set WPS service
   $ export WPS_SERVICE=http://localhost:5000/wps

   # show available processes
   $ birdy -h
   Usage: birdy [OPTIONS] COMMAND [ARGS]...

     Birdy is a command line client for Web Processing Services.

     Documentation is available on readthedocs:
     http://birdy.readthedocs.org/en/latest/

   Options:
     --version         Show the version and exit.
     --cert TEXT       Client side certificate containing both certificate and
                       private key.
     -s, --sync        Execute process in sync mode. Default: async mode.
     -t, --token TEXT  Token to access the WPS service.
     -h, --help        Show this message and exit.

   Commands:
     ultimate_question         Answer to the ultimate question: This process...
     sleep                     Sleep Process: Testing a long running...
     nap                       Afternoon Nap (supports sync calls only):...
     bbox                      Bounding box in- and out: Give bounding box,...
     hello                     Say Hello: Just says a friendly Hello.Returns...

Configure SSL verification for HTTPS
------------------------------------

In case you are a WPS serive using HTTPS with a self-signed certificate you need to configure
the environment variable ``WPS_SSL_VERIFY``:

.. code-block:: sh

  $ export WPS_SSL_VERIFY=false  # deactivate SSL server validation for a self-signed certificate.

You can also set the path of the service certificate.
Read the `requests documentation <http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification>`_.


Use client certificate to access WPS service
--------------------------------------------

If the WPS service is secured by x509 certificates you can add a certificate
with the ``--cert`` option to a request.

.. code-block:: sh

   # set WPS service
   $ export WPS_SERVICE=https://localhost:5000/ows/proxy/emu
   $ export WPS_SSL_VERIFY=false  # deactivate SSL server validation for a self-signed certificate.
   # available processes
   $ birdy -h
   # details of the "hello" process
   $ birdy hello -h
   # run hello with certificate
   $ birdy --cert cert.pem hello --name tux


Using the console
=================

.. automodule:: birdy.native
