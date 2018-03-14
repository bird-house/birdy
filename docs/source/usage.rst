.. _usage:

*****
Usage
*****

Using the command line
======================

Get a list of available processes on WPS with URL http://localhost:8094/wps:

.. code-block:: sh

   # set WPS service
   $ export WPS_SERVICE=http://localhost:8094/wps

   # show available processes
   $ birdy -h
   usage: birdy [-h <command> [<args>]

   optional arguments:
     -h, --help            show this help message and exit

   command:
     List of available commands (wps processes)

     {helloworld,ultimatequestionprocess,wordcount,inout,multiplesources,chomsky,zonal_mean}
                           Run "birdy <command> -h" to get additional help.



Use client certificate to access WPS service
============================================

If the WPS service is secured by x509 certificates you can add a certificate
with the ``--cert`` option to a request.

.. code-block:: sh

   # set WPS service
   $ export WPS_SERVICE=https://localhost:5000/ows/proxy/emu
   # available processes
   $ birdy -h
   # details of the "hello" process
   $ birdy hello -h
   # run hello with certificate
   $ birdy --cert cert.pem hello --name tux
