.. _development:

***********
Development
***********

Install sources
===============

Check out code from the birdy GitHub repo and start the installation:

.. code-block:: sh

   $ git clone https://github.com/bird-house/birdy.git
   $ cd birdy
   $ conda env create -f environment.yml
   $ python setup.py develop

Install additional dependencies::

  $ pip install -r requirements_dev.txt

Build Sphinx documentation
==========================

Use the Makefile::

    $ make docs

Bump a new version
===================

Make a new version of Birdy in the following steps:

* Make sure everything is commit to GitHub.
* Update ``CHANGES.rst`` with the next version.
* Dry Run: ``bumpversion --dry-run --verbose --new-version 0.3.1 patch``
* Do it: ``bumpversion --new-version 0.3.1 patch``
* ... or: ``bumpversion --new-version 0.4.0 minor``
* Push it: ``git push --tags``

See the bumpversion_ documentation for details.

.. _bumpversion: https://pypi.org/project/bumpversion/
