# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup
from pathlib import Path
import re

with open(Path(__file__).parent / 'birdy' / '__init__.py', 'r') as f:
    version = re.search(r'__version__ = [\'"](.+?)[\'"]', f.read()).group(1)

description = 'Birdy provides a command-line tool to work with Web Processing Services.'
long_description = (
    open('README.rst').read() + '\n' + open('AUTHORS.rst').read() + '\n' + open('CHANGES.rst').read()
)

requires = [line.strip() for line in open('requirements.txt')]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
]

setup(name='birdhouse-birdy',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=classifiers,
      keywords='wps pywps python birdy birdhouse',
      author='Birdhouse',
      author_email="wps-dev@dkrz.de",
      url='https://github.com/bird-house/birdy',
      license="Apache License v2.0",
      packages=find_packages(),
      include_package_data=True,
      install_requires=requires,
      entry_points={
          'console_scripts': [
              'birdy=birdy.cli.run:cli']},
      )
