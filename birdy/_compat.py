import logging
import sys

LOGGER = logging.getLogger('BIRDY')
PY2 = sys.version_info[0] == 2

if PY2:
    LOGGER.debug('Python 2.x')
    text_type = unicode  # noqa
    # from StringIO import StringIO
    from urlparse import urlparse
    from urlparse import urlsplit
    from urlparse import urljoin
    # from urllib2 import urlopen

else:
    LOGGER.debug('Python 3.x')
    text_type = str
    # from io import StringIO
    from urllib.parse import urlparse
    from urllib.parse import urlsplit
    from urllib.parse import urljoin
    # from urllib.request import urlopen
