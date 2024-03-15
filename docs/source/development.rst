.. highlight:: shell

***********
Development
***********

Get Started!
============

Check out code from the birdy GitHub repo and start the installation::

    $ git clone https://github.com/bird-house/birdy.git
    $ cd birdy
    $ conda env create -f environment.yml
    $ pip install --editable .

Install additional dependencies::

    $ pip install -r requirements_dev.txt

When you're done making changes, check that your changes pass `black`, `flake8` and the tests::

    $ flake8 birdy tests
    $ black --check --target-version py39 birdy tests
    $ pytest -v tests

Or use the Makefile::

     $ make lint
     $ make test
     $ make test-all

Add pre-commit hooks
--------------------

Before committing your changes, we ask that you install `pre-commit` in your environment.
`Pre-commit` runs git hooks that ensure that your code resembles that of the project
and catches and corrects any small errors or inconsistencies when you `git commit`::

     $ conda install -c conda-forge pre-commit
     $ pre-commit install

Write Documentation
===================

You can find the documentation in the `docs/source` folder. To generate the Sphinx
documentation locally you can use the `Makefile`::

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

Build a source distribution and wheel
=====================================

To build a source distribution (`.sdist`) and wheel (`.whl`) locally, run the following command::

    $ python -m build

This will create a `dist` folder with the source distribution and wheel.

See the `build`_ documentation for details.

.. _build: https://build.pypa.io/en/latest/

Release a new version
=====================

Leveraging GitHub Workflows, maintainers can release new versions of Birdy automatically:

* Ensure that the changelog and version on the main development branch have been updated to reflect the new version.
* Create a tag (`vX.Y.Z`) of the main development branch and push to the GitHub repository.
    * This will trigger a workflow that will attempt to build Birdy and publish it to TestPyPI.
    * When this actions succeeds, be sure to verify on TestPyPI that the package reflects changes.
* On GitHub, a maintainer can then publish a new version using the newly created tag.
    * This will trigger a workflow that will attempt to build Birdy and publish it to PyPI.
    * Be warned that once published to PyPI, a version number can never be overwritten! Bad versions may only be `yanked <https://pypi.org/help/#yanked>`_.
