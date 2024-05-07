Change History
**************

v0.8.7 (2024-05-07)
===================

* Fix regression, where loading TIFF files would return a Dataset instead of a DataArray, the behavior prior to 0.8.5. Loading a multi-band TIFF file will now return a DataArray with the bands as dimensions.


v0.8.6 (2024-03-18)
===================

Changes:

* Restructure the package so that the wheel does not install the testing and docs as non-importable packages.
* Ensure that data required to run tests and build docs is present in the source distribution (via `Manifest.in` changes).
* Documentation now includes a `sphinx-apidoc`-based listing of all installed modules and functions
* Add `sphinx-copybutton` and `sphinx-codeautolink` in order to increase the usefulness of code-blocks in the example documentation (copying of code blocks and ability to click on `birdy` objects and go straight to the documentation entry for the object).
* All documentation build warnings have been addressed.
* Add the `birdy[extra]` pip install recipe to be able to install all extras needed more directly.
* Raise the minimum Python required to 3.9 in the setup block.
* Remove the Python package for `pandoc` (unmaintained).
* Add a documentation entry on using `build` to build the documentation.

0.8.5 (2024-03-14)
==================

Changes:

* Update how TIFF files are converted to xarray datasets because `open_rasterio` is deprecated. See issue `239`.
* Remove `GeotiffRasterioConverter`.
* Remove Python 3.7 and 3.8 from CI test suite.
* Now using Trusted Publisher for TestPyPI/PyPI releases.
* Update `black` to v24.2.0 and code formatting conventions to Python3.9+.

0.8.4 (2023-05-24)
==================

Changes:

* Fix docstring creation error occurring when the server identification abstract is None. See issue `228`.
* Handle case where the server `describeProcess` does not understand "ALL" as the process identifier. See issue `229`.

0.8.3 (2023-05-03)
==================

Changes:

* Added the `packaging` library to the list of requirements.

0.8.2 (2023-04-28)
==================

Changes:

* Relax dependency check on GeoTiff rioxarray and rasterio converters due to some mysterious gdal error.
* Remove tests with live 52North WPS server since it seems offline.
* Remove Python 3.6 from test matrix and add 3.10.
* Handle the removal of the `verbose` argument in `OWSLib.WebProcessingService` 0.29.0.

0.8.1 (2021-12-01)
==================

Changes:

* Before trying to open a netCDF dataset, determine whether link is a valid OPeNDAP endpoint to avoid unnecessarily raising the cryptic ``syntax error, unexpected WORD_WORD, expecting SCAN_ATTR or SCAN_DATASET or SCAN_ERROR``.


0.8.0 (2021-05-25)
==================

Changes:

* Added a converter for loading GeoTIFF using xarray/rioxarray (#193).
* Update notebook process forms. See `client.gui` function.
* Add support for Path objects in `utils.guess_type`.
* Support multiple mimetypes in converters.
* Removed geojson mimetypes from BINARY_MIMETYPES so it's embedded as a string rather than bytes.

API changes:

* `mimetype` (str) replaced by `mimetypes` (tuple) in `client.converters.BaseConverter`.


0.7.0 (2021-01-15)
==================

Changes:

* Added multiple language support (#164).
* Added an Ipyleaflet wrapper for WFS support (#179).
* Updated GeoJSON mimetype (#181).
* Added ability to specify output format for process execution (#182).
* Fixed tests (#184).
* Use GitHub Actions for CI build instead of Travis CI (#185).
* Use black formatting (#186, #187).

0.6.9 (2020-03-10)
==================

Changes:

* Fixed passing Path objects (#169)
* Trying to guess mime type of inputs rather than taking the first value (#171)

0.6.6 (2020-03-03)
==================

Changes:

* Fixed the docs (#150).
* Added outputs to execute in CLI (#151).
* Updated tests (#152).
* Added offline tests (#153).
* Updated conda links (#155).
* Handle Python keywords (#158)
* Fix emu (#159).
* Updated demo notebook tests (#160).
* Added ECMWF demo notebook (#162).
* Added roocs wps demo notebook (#165).
* Added missing files in MANIFEST.in for pypi install (#166).

0.6.5 (2019-08-19)
==================

Changes:

* Fix arguments ordering (#139).
* Fix imports warning (#138).
* Using nbsphinx (#142).
* Fix pip install (#143).
* Add custom authentication methods (#144).
* Use oauth token (#145).
* Skip Python 2.7 (#146).

0.6.4 (2019-07-03)
==================

Changes:

* Fix default converter to return bytes (#137).

0.6.3 (2019-06-21)
==================

Changes:

* Disabled segmented metalink downloads (#132).
* Fix nested conversion (#135).

0.6.2 (2019-06-06)
==================

Changes:

* Added support for passing sequences (list, tuple) as WPS inputs (#128).

0.6.1 (2019-05-27)
==================

Changes:

* Added verify argument when downloading files to disk (#123).
* Bugfixes: #118, #121

0.6.0 (2019-04-04)
==================

Changes:

* Added conversion support for nested outputs (metalink, zip) (#114).
* Added support for Metalink (#113).
* Added support for zip converter (#111).
* Added support for ESGF CWT API (#102).
* Speed up by using `DescribeProcess` with `identifier=all` (#98).
* Added support for passing local files to server as raw data (#97).
* Cleaned up notebooks (#107).
* Various Bugfixes: #83, #91, #99

0.5.1 (2018-12-18)
==================

Changes:

* Added support to launch Jupyter notebooks with birdy examples on binder (#94, #95).

0.5.0 (2018-12-03)
==================

Changes:

* Renamed pythonic WPS client (#63): ``birdy.client.base.WPSClient`` and ``from birdy import WPSClient``.
* Added `WPSResult` for WPS outputs as `namedtuple` (#84, #64).
* Support for Jupter Notebooks (#40): cancel button (work in progress), progress bar, input widget.
* Updated notebooks with examples for `WPSClient`.

0.4.2 (2018-09-26)
==================

Changes:

* Fixed WPS default parameter (#52).
* Using ``WPS_SSL_VERIFY`` environment variable (#50).

0.4.1 (2018-09-14)
==================

Changes:

* Fixed test-suite (#49).
* Import native client with ``import_wps`` (#47).
* Fix: using string type when dataType is not provided (#46).
* Updated docs for native client (#43).

0.4.0 (2018-09-06)
==================

Release for Dar Es Salaam.

Changes:

* Conda support on RTD (#42).
* Fix optional input (#41).

0.3.3 (2018-07-18)
==================

Changes:

* Added initial native client (#24, #37).

0.3.2 (2018-06-06)
==================

Changes:

* Fix MANIFEST.in.

0.3.1 (2018-06-06)
==================

Changes:

* Fix bumpversion.

0.3.0 (2018-06-05)
==================

Changes:

* Use bumpversion (#29).
* Use click for CLI (#6).
* Using GitHub templates for issues, PRs and contribution guide.

0.2.2 (2018-05-08)
==================

Fixes:

* Update travis for Python 3.x (#19).
* Fix parsing of WPS capabilities with ``%`` (#18).

New Features:

* using ``mode`` for async execution in OWSLib (#22).

0.2.1 (2018-03-14)
==================

Fixes:

* Fixed Sphinx and updated docs: #15.

New Features:

* Fix #14: added ``--cert`` option to use x509 certificates.

0.2.0 (2017-09-25)
==================

* removed buildout ... just using conda.
* cleaned up docs.
* updated travis.
* fixed tests.
* added compat module for python 3.x

0.1.9 (2017-04-07)
==================

* updated buildout and Makefile.
* updated conda environment.
* fixed tests.
* replaced nose by pytest.
* pep8.
* fixed travis.
* fixed ComplexData input.
* show status message in log.

0.1.8 (2016-05-02)
==================

* added backward compatibility for owslib.wps without headers and verify parameter.

0.1.7 (2016-05-02)
==================

* added twitcher token parameter.
* using ssl verify option again.

0.1.6 (2016-03-22)
==================

* added support for bbox parameters.

0.1.5 (2016-03-15)
==================

* fixed wps init (using standard owslib).
* update makefile.

0.1.4 (2015-10-29)
==================

* using ssl verify option of WebProcessingSerivce
* moved python requirements to requirements/deploy.txt

0.1.3 (2015-08-20)
==================

* more unit tests.
* fixed unicode error in wps description.
* using latest ComplexDataInput from owslib.wps.

0.1.2 (2015-08-14)
==================

* fixed encoding of input text files.
* more unit tests.

0.1.1 (2015-08-13)
==================

* allow local file path for complex inputs.
* send complex data inline with requet to remote wps service.

0.1.0 (2014-12-02)
==================

* Initial Release.
