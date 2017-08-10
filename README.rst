=====
Birdy
=====

.. image:: https://travis-ci.org/bird-house/birdy.svg?branch=master
   :target: https://travis-ci.org/bird-house/birdy
   :alt: Travis Build


Birdy (the bird)
   *Birdy is not a bird but likes to play with them.*

Birdy is a Python command-line tool to work with Web Processing Services (WPS).
It is using OWSLib from the GeoPython project.

Birdy is part of the `Birdhouse <http://bird-house.github.io/>`_ project.

Install from Anaconda
=====================

.. image:: http://anaconda.org/birdhouse/birdhouse-birdy/badges/installer/conda.svg
   :target: http://anaconda.org/birdhouse/birdhouse-birdy
   :alt: Ananconda Install

.. image:: http://anaconda.org/birdhouse/birdhouse-birdy/badges/build.svg
   :target: http://anaconda.org/birdhouse/birdhouse-birdy
   :alt: Anaconda Build

.. image:: http://anaconda.org/birdhouse/birdhouse-birdy/badges/version.svg
   :target: http://anaconda.org/birdhouse/birdhouse-birdy
   :alt: Anaconda Version

.. image:: http://anaconda.org/birdhouse/birdhouse-birdy/badges/downloads.svg
   :target: http://anaconda.org/birdhouse/birdhouse-birdy
   :alt: Anaconda Downloads

.. code-block:: sh

   $ conda install -c birdhouse birdhouse-birdy

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

Full `documentation <http://birdy.readthedocs.org/en/latest/>`_ is on ReadTheDocs.
