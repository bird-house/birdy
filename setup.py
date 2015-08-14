# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

version = '0.1.2'
description = 'Birdy provides a command-line tool to work with Web Processing Services (WPS).'
long_description = (
    open('README.rst').read() + '\n' +
    open('AUTHORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

requires = [
    'argcomplete',
    'lxml',
    'owslib',
    'nose',
    ]

classifiers=[
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
      keywords='wps pywps python birdy netcdf esgf birdhouse anaconda',
      author='Birdhouse',
      url='https://github.com/bird-house/birdy',
      license = "Apache License v2.0",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=requires,
      entry_points = {
          'console_scripts': [
              'birdy=birdy:main',
              'esgsearch=birdy.esgsearch:main'
              ]}     
      ,
      )
