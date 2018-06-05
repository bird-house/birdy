.DEFAULT_GOAL := help

.PHONY: all
all: help

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  help        to print this help message. (Default)"
	@echo "  test        to run tests (but skip long running tests)."
	@echo "  testall     to run all tests (including long running tests)."
	@echo "  pep8        to run pep8 code style checks."
	@echo "  docs        to generate the Sphinx documentation."
	@echo "  clean       to remove all *.pyc files."
	@echo "  distclean   to remove *all* files that are not controlled by 'git'. WARNING: use it *only* if you know what you do!"


.PHONY: clean
clean: srcclean

.PHONY: srcclean
srcclean:
	@echo "Removing *.pyc files ..."
	@-find . -type f -name "*.pyc" -print | xargs rm

.PHONY: distclean
distclean: clean
	@echo "Cleaning distribution ..."
	@git diff --quiet HEAD || echo "There are uncommited changes! Not doing 'git clean' ..."
	@-git clean -dfx

PHONY: bootstrap_dev
bootstrap_dev:
	@echo "Installing development requirements for tests and docs ..."
	@-bash -c "conda install -y -n birdy pytest flake8 sphinx bumpversion"
	@-bash -c "pip install -r requirements_dev.txt"

.PHONY: test
test:
	@echo "Running tests (skip slow and online tests) ..."
	pytest -v -m 'not slow and not online'

.PHONY: testall
testall:
	@echo "Running all tests (including slow and online tests) ..."
	pytest -v

.PHONY: pep8
pep8:
	@echo "Running pep8 code style checks ..."
	flake8

.PHONY: docs
docs:
	@echo "Generating docs with Sphinx ..."
	$(MAKE) -C $@ clean html
	@echo "open your browser: open docs/build/html/index.html"
