VERSION := 0.2.2
RELEASE := master

# Application
APP_ROOT := $(CURDIR)
APP_NAME := $(shell basename $(APP_ROOT))

# guess OS (Linux, Darwin, ...)
OS_NAME := $(shell uname -s 2>/dev/null || echo "unknown")
CPU_ARCH := $(shell uname -m 2>/dev/null || uname -p 2>/dev/null || echo "unknown")

# Anaconda 
ANACONDA_HOME ?= $(HOME)/anaconda
CONDA_ENV := birdhouse
CONDA_ENVS_DIR := $(HOME)/.conda/envs
PREFIX := $(CONDA_ENVS_DIR)/$(CONDA_ENV)

# choose anaconda installer depending on your OS
ANACONDA_URL = http://repo.continuum.io/miniconda
ifeq "$(OS_NAME)" "Linux"
FN := Miniconda-latest-Linux-x86_64.sh
else ifeq "$(OS_NAME)" "Darwin"
FN := Miniconda-3.7.0-MacOSX-x86_64.sh
else
FN := unknown
endif

# Buildout files and folders
DOWNLOAD_CACHE := $(APP_ROOT)/downloads
BUILDOUT_FILES := parts eggs develop-eggs bin .installed.cfg .mr.developer.cfg *.egg-info bootstrap-buildout.py *.bak.* $(DOWNLOAD_CACHE)

# Docker
DOCKER_IMAGE := birdhouse/$(APP_NAME)
DOCKER_CONTAINER := $(APP_NAME)

# end of configuration

.DEFAULT_GOAL := all

.PHONY: all
all: sysinstall clean install
	@echo "\nRun 'make help' for a description of all make targets."
	@echo "Read also the README.rst on GitHub: https://github.com/bird-house/birdhousebuilder.bootstrap"

.PHONY: help
help:
	@echo "make [target]\n"
	@echo "targets:\n"
	@echo "\t all         \t- Does a complete installation. Shortcut for 'make sysinstall clean install.' (Default)"
	@echo "\t help        \t- Prints this help message."
	@echo "\t version     \t- Prints version number of this Makefile."
	@echo "\t info        \t- Prints information about your system."
	@echo "\t install     \t- Installs your application by running 'bin/buildout -c custom.cfg'."
	@echo "\t test        \t- Run tests (but skip long running tests)."
	@echo "\t testall     \t- Run all tests (including long running tests)."
	@echo "\t clean       \t- Deletes all files that are created by running buildout."
	@echo "\t distclean   \t- Removes *all* files that are not controlled by 'git'.\n\t\t\tWARNING: use it *only* if you know what you do!"
	@echo "\t sysinstall  \t- Installs system packages from requirements.sh. You can also call 'bash requirements.sh' directly."
	@echo "\t docs        \t- Generates HTML documentation with Sphinx."
	@echo "\t selfupdate  \t- Updates this Makefile."
	@echo "\nSupervisor targets:\n"
	@echo "\t start       \t- Starts supervisor service: $(PREFIX)/etc/init.d/supervisord start"
	@echo "\t stop        \t- Stops supervisor service: $(PREFIX)/etc/init.d/supervisord stop"
	@echo "\t restart     \t- Restarts supervisor service: $(PREFIX)/etc/init.d/supervisord restart"
	@echo "\t status      \t- Supervisor status: $(PREFIX)/bin/supervisorctl status"
	@echo "\nDocker targets:\n"
	@echo "\t Dockerfile  \t- Generates a Dockerfile for this application."
	@echo "\t dockerbuild \t- Build a docker image for this application."

.PHONY: version
version:
	@echo "Version: $(VERSION)"

.PHONY: info
info:
	@echo "Informations about your System:\n"
	@echo "\t OS_NAME          \t= $(OS_NAME)"
	@echo "\t CPU_ARCH         \t= $(CPU_ARCH)"
	@echo "\t Anaconda         \t= $(FN)"
	@echo "\t Anaconda Home    \t= $(ANACONDA_HOME)"
	@echo "\t Birdhouse Env    \t= $(PREFIX)"
	@echo "\t APP_NAME         \t= $(APP_NAME)"
	@echo "\t APP_ROOT         \t= $(APP_ROOT)"
	@echo "\t DOWNLOAD_CACHE   \t= $(DOWNLOAD_CACHE)"
	@echo "\t DOCKER_IMAGE     \t= $(DOCKER_IMAGE)"
	@echo "\t DOCKER_CONTAINER \t= $(DOCKER_CONTAINER)"

## Helper targets ... ensure that Makefile etc are in place

.PHONY: backup
backup:
	@echo "Backup custom config ..." 
	@-test -f custom.cfg && cp -v --update --backup=numbered --suffix=.bak custom.cfg custom.cfg.bak

.gitignore:
	@echo "Setup default .gitignore ..."
	@wget -q --no-check-certificate -O .gitignore "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/$(RELEASE)/dot_gitignore"

bootstrap.sh:
	@echo "Update bootstrap.sh ..."
	@wget -q --no-check-certificate -O bootstrap.sh "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/$(RELEASE)/bootstrap.sh"
	@chmod 755 bootstrap.sh

requirements.sh:
	@echo "Setup default requirements.sh ..."
	@wget -q --no-check-certificate -O requirements.sh "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/$(RELEASE)/requirements.sh"
	@chmod 755 requirements.sh

custom.cfg:
	@echo "Using custom.cfg for buildout ..."
	@test -f custom.cfg || cp -v custom.cfg.example custom.cfg

.PHONY: downloads
downloads:
	@echo "Using DOWNLOAD_CACHE = ${DOWNLOAD_CACHE}"
	@test -d $(DOWNLOAD_CACHE) || mkdir -v -p $(DOWNLOAD_CACHE)

.PHONY: init
init: .gitignore custom.cfg downloads

bootstrap-buildout.py:
	@echo "Update buildout bootstrap-buildout.py ..."
	@test -f boostrap-buildout.py || wget --no-check-certificate -O bootstrap-buildout.py https://bootstrap.pypa.io/bootstrap-buildout.py

## Anaconda targets

.PHONY: anaconda
anaconda:
	@echo "Installing Anaconda ..."
	@test -d $(ANACONDA_HOME) || wget -q -c -O "$(DOWNLOAD_CACHE)/$(FN)" $(ANACONDA_URL)/$(FN)
	@test -d $(ANACONDA_HOME) || bash "$(DOWNLOAD_CACHE)/$(FN)" -b -p $(ANACONDA_HOME)   
	@echo "Add '$(ANACONDA_HOME)/bin' to your PATH variable in '.bashrc'."

.PHONY: conda_config
conda_config: anaconda
	@echo "Update ~/.condarc"
	@"$(ANACONDA_HOME)/bin/conda" config --add envs_dirs $(CONDA_ENVS_DIR)
	@"$(ANACONDA_HOME)/bin/conda" config --set ssl_verify false
	@"$(ANACONDA_HOME)/bin/conda" config --add channels defaults
	@"$(ANACONDA_HOME)/bin/conda" config --add channels birdhouse
	@"$(ANACONDA_HOME)/bin/conda" config --add channels pingucarsti

.PHONY: conda_env
conda_env: anaconda conda_config
	@test -d $(PREFIX) || "$(ANACONDA_HOME)/bin/conda" create -m -p $(PREFIX) -c birdhouse --yes python=2.7.8 setuptools pyopenssl genshi mako

.PHONY: conda_pinned
conda_pinned: conda_env
	@echo "Update pinned conda packages ..."
	@test -d $(PREFIX) && wget -q -c -O "$(PREFIX)/conda-meta/pinned" https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/master/conda_pinned 

.PHONY: conda_clean
conda_clean: anaconda conda_config
	@test -d $(PREFIX) && "$(ANACONDA_HOME)/bin/conda" env remove -n $(CONDA_ENV) 

## Build targets

.PHONY: bootstrap
bootstrap: init conda_env conda_pinned bootstrap-buildout.py
	@echo "Bootstrap buildout ..."
	@-test -f bin/buildout || "$(ANACONDA_HOME)/bin/conda" remove -y -n $(CONDA_ENV) curl setuptools
	@test -f bin/buildout || bash -c "source $(ANACONDA_HOME)/bin/activate $(CONDA_ENV);python bootstrap-buildout.py -c custom.cfg --allow-site-packages"

.PHONY: sysinstall
sysinstall: bootstrap.sh requirements.sh
	@echo "\nInstalling system packages for bootstrap ..."
	@bash bootstrap.sh -i
	@echo "\nInstalling system packages for your application ..."
	@bash requirements.sh

.PHONY: install
install: bootstrap
	@echo "Installing application with buildout ..."
	bash -c "source $(ANACONDA_HOME)/bin/activate $(CONDA_ENV);bin/buildout -c custom.cfg"

.PHONY: build
build: install
	@echo "\nPlease use 'make install' instead of 'make build'"

.PHONY: clean
clean:
	@echo "Cleaning buildout files ..."
	@-for i in $(BUILDOUT_FILES); do \
            test -e $$i && rm -v -rf $$i; \
        done

.PHONY: distclean
distclean: backup clean
	@echo "Cleaning distribution ..."
	@git diff --quiet HEAD || echo "There are uncommited changes! Not doing 'git clean' ..."
	@-git clean -dfx --exclude=*.bak

.PHONY: buildclean
buildclean:
	@echo "Removing bootstrap.sh ..."
	@test -e bootstrap.sh && rm -v bootstrap.sh

.PHONY: test
test:
	@echo "Running tests (skip slow tests) ..."
	bin/nosetests -a '!slow' unit_tests

.PHONY: testall
testall:
	@echo "Running all tests (include slow tests) ..."
	@echo "Running tests ..."
	bin/nosetests unit_tests

.PHONY: docs
docs:
	@echo "Generating docs with Sphinx ..."
	$(MAKE) -C $@ clean html
	@echo "open your browser: firefox docs/build/html/index.html"

.PHONY: selfupdate
selfupdate: bootstrap.sh
	@wget -q --no-check-certificate -O Makefile "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/$(RELEASE)/Makefile"

## Supervisor targets

.PHONY: start
start:
	@echo "Starting supervisor service ..."
	$(PREFIX)/etc/init.d/supervisord start

.PHONY: stop
stop:
	@echo "Stopping supervisor service ..."
	$(PREFIX)/etc/init.d/supervisord stop

.PHONY: restart
restart:
	@echo "Restarting supervisor service ..."
	$(PREFIX)/etc/init.d/supervisord restart

.PHONY: status
status:
	@echo "Supervisor status ..."
	$(PREFIX)/bin/supervisorctl status


## Docker targets

.dockerignore:
	@echo "Update .dockerignore ..."
	@wget -q --no-check-certificate -O .dockerignore "https://raw.githubusercontent.com/bird-house/birdhousebuilder.bootstrap/master/dot_dockerignore"

.PHONY: Dockerfile
Dockerfile: bootstrap
	@echo "Update Dockerfile ..."
	bin/buildout -c custom.cfg install docker

.PHONY: dockerrmi
dockerrmi: 
	@echo "Removing previous docker image ..."
	docker rmi $(DOCKER_IMAGE)

.PHONY: dockerbuild
dockerbuild: Dockerfile .dockerignore
	@echo "Building docker image ..."
	docker build --rm -t $(DOCKER_IMAGE) .

.PHONY: dockerrun
dockerrun: dockerbuild
	@echo "Run docker image ..."
	docker run -i -t -p 9001:9001 --name=$(DOCKER_CONTAINER) $(DOCKER_IMAGE) /bin/bash
