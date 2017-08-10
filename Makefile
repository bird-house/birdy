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
	@echo "  clean    to remove all *.pyc files."
	@echo "  distclean   to remove *all* files that are not controlled by 'git'. WARNING: use it *only* if you know what you do!"


.PHONY: clean
clean: srcclean

.PHONY: srcclean
srcclean:
	@echo "Removing *.pyc files ..."
	@-find $(APP_ROOT) -type f -name "*.pyc" -print | xargs rm

.PHONY: distclean
distclean: clean
	@echo "Cleaning distribution ..."
	@git diff --quiet HEAD || echo "There are uncommited changes! Not doing 'git clean' ..."
	@-git clean -dfx

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
