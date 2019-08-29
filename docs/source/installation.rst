.. _installation:

************
Installation
************

Install from Anaconda
=====================

.. image:: https://anaconda.org/conda-forge/birdy/badges/installer/conda.svg
   :target: https://anaconda.org/conda-forge/birdy
   :alt: Ananconda Install

.. image:: https://anaconda.org/conda-forge/birdy/badges/version.svg
   :target: https://anaconda.org/conda-forge/birdy
   :alt: Anaconda Version

.. image:: https://anaconda.org/conda-forge/birdy/badges/downloads.svg
   :target: https://anaconda.org/conda-forge/birdy
   :alt: Anaconda Downloads

.. code-block:: console

   $ conda install -c conda-forge birdy

Install from GitHub
===================

Check out code from the birdy GitHub repo and start the installation:

.. code-block:: console

   $ git clone https://github.com/bird-house/birdy.git
   $ cd birdy
   $ conda env create -f environment.yml
   $ python setup.py install
