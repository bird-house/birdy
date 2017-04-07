Change History
**************

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
