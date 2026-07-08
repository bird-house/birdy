============
Installation
============

If you don't have `pip`_ installed, this `Python installation guide`_ can guide you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Stable release
--------------

To install birdy, run this command in your terminal:

.. code-block:: console

    python -m pip install birdhouse-birdy

..
    .. code-block:: console

        conda install birdy

This is the preferred method to install birdy, as it will always install the most recent stable release.


From sources
------------

The sources for birdy can be downloaded from the `Github repo`_.

#. Download the source code from the `Github repo`_ using one of the following methods:

    * Clone the public repository:

        .. code-block:: console

            git clone git@github.com:bird-house/birdy.git

    * Download the `tarball <https://github.com/bird-house/birdy/tarball/main>`_:

        .. code-block:: console

            curl -OJL https://github.com/bird-house/birdy/tarball/main

#. Once you have a copy of the source, you can install it with:

    .. code-block:: console

        python -m pip install .

   Or, alternatively:

    .. code-block:: console

        conda env create -f environment-dev.yml
        conda activate birdy-dev
        make dev

    If you are on Windows, replace the ``make dev`` command with the following:

    .. code-block:: console

        python -m pip install -e .[dev]

    Even if you do not intend to contribute to `birdy`, we favor using `environment-dev.yml` over `environment.yml` because it includes additional packages that are used to run all the examples provided in the documentation.
    If for some reason you wish to install the `PyPI` version of `birdy` into an existing Anaconda environment (*not recommended if requirements are not met*), only run the last command above.

#. When new changes are made to the `Github repo`_, if using a clone, you can update your local copy using the following commands from the root of the repository:

    .. code-block:: console

        git fetch
        git checkout main
        git pull origin main
        python -m pip install .


    These commands should work most of the time, but if big changes are made to the repository, you might need to remove the environment and create it again.

.. _Github repo: https://github.com/bird-house/birdy
