Change History
**************

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
