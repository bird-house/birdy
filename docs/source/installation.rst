.. _installation:

************
Installation
************

Install from Anaconda
=====================

.. image:: http://anaconda.org/birdhouse/birdhouse-birdy/badges/installer/conda.svg
   :target: http://anaconda.org/birdhouse/birdhouse-birdy
   :alt: Ananconda Install

.. image:: http://anaconda.org/birdhouse/birdhouse-birdy/badges/version.svg
   :target: http://anaconda.org/birdhouse/birdhouse-birdy
   :alt: Anaconda Version

.. image:: http://anaconda.org/birdhouse/birdhouse-birdy/badges/downloads.svg
   :target: http://anaconda.org/birdhouse/birdhouse-birdy
   :alt: Anaconda Downloads

.. code-block:: sh

   $ conda install -c birdhouse -c conda-forge birdhouse-birdy

Install from GitHub
===================

Check out code from the birdy GitHub repo and start the installation:

.. code-block:: sh

   $ git clone https://github.com/bird-house/birdy.git
   $ cd birdy
   $ conda env create -f environment.yml
   $ python setup.py install

Using bash completion
+++++++++++++++++++++

You can enable bash completion for Birdy by using the following script::

  $ . birdy-complete.sh

For details read the `Click documentation <http://click.pocoo.org/6/bashcomplete/>`_.
