.. _installation:

************
Installation
************

Install from PyPI
=================

|pypi|

.. code-block:: console

    $ pip install birdhouse-birdy

Install from Anaconda
=====================

|conda install| |conda version| |conda downloads|

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


.. |pypi| image:: https://img.shields.io/pypi/v/birdhouse-birdy.svg
        :target: https://pypi.python.org/pypi/birdhouse-birdy
        :alt: Python Package Index Build

.. |conda install| image:: https://anaconda.org/conda-forge/birdy/badges/installer/conda.svg
        :target: https://anaconda.org/conda-forge/birdy
        :alt: Anaconda Install

.. |conda version| image:: https://anaconda.org/conda-forge/birdy/badges/version.svg
        :target: https://anaconda.org/conda-forge/birdy
        :alt: Anaconda Version

.. |conda downloads| image:: https://anaconda.org/conda-forge/birdy/badges/downloads.svg
        :target: https://anaconda.org/conda-forge/birdy
        :alt: Anaconda Downloads
