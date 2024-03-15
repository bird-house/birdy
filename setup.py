# noqa: D100

import re
from pathlib import Path

from setuptools import find_namespace_packages, setup


def parse_reqs(file):
    """Parse dependencies from requirements file with regex."""
    egg_regex = re.compile(r"#egg=(\w+)")
    reqs = list()
    for req in open(file):
        req = req.strip()
        git_url_match = egg_regex.search(req)
        if git_url_match:
            req = git_url_match.group(1)
        reqs.append(req)
    return reqs


with open(Path(__file__).parent / "birdy" / "__init__.py") as f:
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
extra_requirements = parse_reqs("requirements_extra.txt")

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
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
    python_requires=">=3.9.0",
    packages=find_namespace_packages(exclude=["docs", "docs.*", "tests", "tests.*"]),
    include_package_data=True,
    package_data={
        "birdy": ["ipyleafletwps/examples/*.ipynb"],
    },
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,  # pip install ".[dev]"
        "extra": extra_requirements,  # pip install ".[extra]"
    },
    entry_points={"console_scripts": ["birdy=birdy.cli.run:cli"]},
    zip_safe=False,
)
