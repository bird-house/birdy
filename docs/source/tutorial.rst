.. _tutorial:

Example Usage
=============

Show the processes of a Web Processing Service:

.. code-block:: sh

   $ export WPS_SERVICE=http://localhost:8094/wps
   $ birdy -h
   usage: birdy [<options>] <command> [<args>]
    
   Emu: WPS processes for testing and demos.
    
   optional arguments:
     -h, --help            show this help message and exit
     --debug               enable debug mode
     --token TOKEN, -t TOKEN
                           Token to access the WPS service.

    
   command:
     List of available commands (wps processes)
    
     {helloworld,ultimatequestionprocess,wordcount,inout,multiplesources,chomsky,zonal_mean}
                           Run "birdy <command> -h" to get additional help.
       helloworld          Hello World: Welcome user and say hello ...
       ultimatequestionprocess
                           Answer to Life, the Universe and Everything: Numerical
                           solution that is the answer to Life, Universe and
                           Everything. The process is an improvement to Deep
                           Tought computer (therefore version 2.0) since it no
                           longer takes 7.5 milion years, but only a few seconds
                           to give a response, with an update of status every 10
                           seconds.
       wordcount           Word Counter: Counts words in a given text ...
       inout               Testing all Data Types: Just testing data types like
                           date, datetime etc ...
       multiplesources     Multiple Sources: Process with multiple different
                           sources ...
       chomsky             Chomsky text generator: Generates a random chomsky
                           text ...
       zonal_mean          Zonal Mean: zonal mean in NetCDF File.


Show help for wordcount:

.. code-block:: sh

    $ birdy wordcount -h
    usage: birdy wordcount [-h] --text [TEXT] [--output [{output} [{output} ...]]]
     
    optional argumens:
      -h, --help            show this help message and exit
      --text [TEXT]         Text document: URL of text document, mime
                            types=text/plain
      --output [{output} [{output} ...]]
                            Output: output=Word count result, mime
                            types=text/plain (default: all outputs) 
     

Execute wordcount with a remote text document:

.. code-block:: sh

    $ birdy wordcount --text http://birdy.readthedocs.org/en/latest/tutorial.html
    INFO:Execution status: ProcessAccepted
    INFO:Execution status: ProcessSucceeded
    INFO:Output:
    INFO:output=http://localhost:8090/wpsoutputs/emu/output-7becb14c-41c6-11e5-ae23-68f72837e1b4.txt (text/plain)

The result output is given as a reference document.


You can also use a local file as input document:

.. code-block:: sh

    $ birdy wordcount --text /usr/share/doc/gimp-help-en/html/en/index.html 
    INFO:Execution status: ProcessAccepted
    INFO:Execution status: ProcessSucceeded
    INFO:Output:
    INFO:output=http://localhost:8090/wpsoutputs/emu/output-f65f5358-41c6-11e5-ae23-68f72837e1b4.txt (text/plain)


If you run this process on a remote WPS service then local files will be send inline and base64 encoded with the WPS execute request. Please use in this case *small files only* (a few megabytes)!

If the WPS service is secured by a Twitcher security proxy service then you can provide an access token with the ``-token`` option:

.. code-block:: sh

    $ birdy --token abc123 wordcount --text http://birdy.readthedocs.org/en/latest/tutorial.html
   

