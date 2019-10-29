# Birdy Examples

JupterLab notebooks with examples for birdy usage.

## Installation

Update birdy conda environment:

    $ conda env update -f environment.yml
    $ source activate birdy

Install JupyterLab widget extension:

    $ jupyter labextension install @jupyter-widgets/jupyterlab-manager


## Start JupyterLab

    $ jupyter lab

## Demo notebooks

Notebooks in the demo folder are run and tested by [pytest](https://pypi.org/project/nbval/).
You can run this test manually with ``make test-nb``.
The notebooks test will always be checked by Travis.
