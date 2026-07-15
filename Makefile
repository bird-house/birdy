.PHONY: clean clean-build clean-pyc clean-test coverage develop dist docs help install lint release test test-nb
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-docs: ## remove docs artifacts
	rm -f docs/apidoc/birdy*.rst
	rm -f docs/apidoc/modules.rst
	$(MAKE) -C docs clean

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr .pytest_cache
	rm -fr .tox/
	rm -fr htmlcov/

install-lint: ## install dependencies needed for linting
	python -m pip install --quiet --group lint

install-docs: ## install dependencies needed for building the docs
	python -m pip install --quiet --group docs

install-test: ## install dependencies needed for standard testing
	python -m pip install --quiet --group test

install-tox: ## install base dependencies needed for running tox
	python -m pip install --quiet --group tox

lint: install-lint ## check style
# 	python -m ruff check src/birdy tests  # FIXME: Enable this check at a later date
	python -m flake8 --config=.flake8 src/birdy tests
	python -m numpydoc lint src/birdy/**.py
	python -m vulture src/birdy tests
	codespell src/birdy tests docs
	python -m deptry src
	python -m yamllint --config-file=.yamllint.yaml src/birdy

test: install-test ## run tests quickly with the default Python
	python -m pytest -v -m 'not slow and not online'

test-nb: install-test ## run notebook tests quickly with the default Python
	pytest --nbval $(CURDIR)/notebooks/demo --sanitize-with $(CURDIR)/notebooks/output_sanitize.cfg

test-all: install-tox ## run tests on every Python version with tox
	python -m tox

coverage: install-test ## check code coverage quickly with the default Python
	python -m coverage run --source src/birdy -m pytest
	python -m coverage report -m
	python -m coverage html
	$(BROWSER) htmlcov/index.html

autodoc: install-docs clean-docs ## create sphinx-apidoc files:
	sphinx-apidoc -o docs/apidoc --private --module-first --separate src/birdy

linkcheck: autodoc ## run checks over all external links found throughout the documentation
	$(MAKE) -C docs linkcheck

build-docs: autodoc ## generate Sphinx HTML documentation, including API docs
	$(MAKE) -C docs html

docs: build-docs  ## open the built documentation in a web browser
ifndef READTHEDOCS
	$(BROWSER) docs/_build/html/index.html
endif

servedocs: autodoc ## compile the docs while watching for changes
	$(MAKE) -C docs livehtml

dist: clean ## builds source and wheel package
	python -m flit build
	ls -l dist

release: dist ## package and upload a release
	python -m flit publish dist/*

install: clean ## install the package to the active Python's site-packages
	python -m pip install --no-user .

develop: clean ## install the package to the active Python's site-packages
	python -m pip install --group dev
	python -m pip install --no-user --editable .[extras]
	prek install
