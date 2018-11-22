.. _tutorial:

********
Tutorial
********

.. contents::
    :local:
    :depth: 2

.. warning::

  To run the examples in this tutorial you will need a running WPS service.

In our examples we use Emu_ installed on ``localhost`` with default settings.

.. toctree::
   :maxdepth: 1

Command line Example
====================

Show the processes of a Web Processing Service:

.. code-block:: sh

   $ export WPS_SERVICE=http://localhost:5000/wps
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
      dummyprocess              Dummy Process: DummyProcess to check the WPS...
      wordcounter               Word Counter: Counts words in a given text.
      chomsky                   Chomsky text generator: Generates a random...
      inout                     In and Out: Testing all WPS input and output...
      binaryoperatorfornumbers  Binary Operator for Numbers: Performs...
      show_error                Show a WPS Error: This process will fail...

Show help for wordcounter:

.. code-block:: sh

    $ birdy wordcounter -h
    Usage: birdy wordcounter [OPTIONS]

      Word Counter: Counts words in a given text.

    Options:
      --version       Show the version and exit.
      --text COMPLEX  Text document
      -h, --help      Show this message and exit.


Execute wordcounter with a remote text document:

.. code-block:: sh

    $ birdy wordcounter --text http://birdy.readthedocs.org/en/latest/tutorial.html
    ProcessSucceeded  [####################################]  100%  0d 00:01:39
    Output:
    output=http://localhost:5000/outputs/0876142e-68c4-11e8-83c7-109836a7cf3a/out_CK146m.txt


The result output is given as a reference document.

Use a Twitcher access token
---------------------------

If the WPS service is secured by a Twitcher security proxy service then you can
provide an access token with the ``--token`` option:

.. code-block:: sh

    $ birdy --token abc123 wordcounter --text http://birdy.readthedocs.org/en/latest/tutorial.html

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

Notebooks with Python Library
=============================

Check the Jupyter notebooks in the `notebooks/` folder
or view `Birdy Notebooks`_ online.

.. _Birdy Notebooks: https://nbviewer.jupyter.org/github/bird-house/birdy/tree/master/notebooks/
