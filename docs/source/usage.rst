.. _usage:

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
