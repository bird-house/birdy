# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup
from pathlib import Path
import re


def parse_reqs(file):
    egg_regex = re.compile(r"#egg=(\w+)")
    reqs = list()
    for req in open(file):
        req = req.strip()
        git_url_match = egg_regex.search(req)
        if git_url_match:
            req = git_url_match.group(1)
        reqs.append(req)
    return reqs


with open(Path(__file__).parent / "birdy" / "__init__.py", "r") as f:
    version = re.search(r'__version__ = [\'"](.+?)[\'"]', f.read()).group(1)

description = "Birdy provides a command-line tool to work with Web Processing Services."
long_description = (
    open("README.rst").read()
    + "\n"
    + open("AUTHORS.rst").read()
    + "\n"
    + open("CHANGES.rst").read()
)

requirements = parse_reqs("requirements.txt")
dev_requirements = parse_reqs("requirements_dev.txt")

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Atmospheric Science",
]

setup(
    name="birdhouse-birdy",
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    classifiers=classifiers,
    keywords="wps pywps owslib geopython birdy birdhouse",
    author="Carsten Ehbrecht",
    author_email="ehbrecht@dkrz.de",
    url="https://github.com/bird-house/birdy",
    license="Apache License v2.0",
    # This qualifier can be used to selectively exclude Python versions -
    # in this case early Python 2 and 3 releases
    python_requires=">=3.6.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,  # pip install ".[dev]"
    },
    entry_points={"console_scripts": ["birdy=birdy.cli.run:cli"]},
)
