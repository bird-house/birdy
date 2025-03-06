.. _installation:

************
Installation
************

Install from PyPI
=================

|pypi| |pypi downloads|

.. code-block:: console

    $ pip install birdhouse-birdy

Install from Anaconda
=====================

|conda version| |conda downloads|

.. code-block:: console

    $ conda install -c conda-forge birdy

Install from GitHub
===================

Check out code from the birdy GitHub repo and start the installation:

.. code-block:: console

    $ git clone https://github.com/bird-house/birdy.git
    $ cd birdy
    $ conda env create -f environment.yml

For a non-interactive installation:

.. code-block:: console

    $ python -m pip install .

Or, for an editable (development) installation:

.. code-block:: console

    $ python -m pip install --editable .

.. |pypi| image:: https://img.shields.io/pypi/v/birdhouse-birdy.svg
        :target: https://pypi.python.org/pypi/birdhouse-birdy
        :alt: Python Package Index Version

.. |pypi downloads| image:: https://img.shields.io/pypi/dm/birdhouse-birdy
        :target: https://pypi.python.org/pypi/birdhouse-birdy
        :alt: Python Package Index Downloads

.. |conda version| image:: https://anaconda.org/conda-forge/birdy/badges/version.svg
        :target: https://anaconda.org/conda-forge/birdy
        :alt: Anaconda Version

.. |conda downloads| image:: https://anaconda.org/conda-forge/birdy/badges/downloads.svg
        :target: https://anaconda.org/conda-forge/birdy
        :alt: Anaconda Downloads
