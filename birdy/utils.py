import urlparse
import base64
from os.path import curdir, abspath, join

import logging
logger = logging.getLogger(__name__)


def fix_local_url(url):
    """
    If url is just a local path name then create a file:// URL. Otherwise return url just as it is.
    """
    logger.debug("fix url %s", url)
    if url is None:
        return None
    u = urlparse.urlsplit(url)
    if not u.scheme:
        # build local file url
        path = u.path.strip()
        if path.startswith('/'):
            # absolute path
            url = urlparse.urljoin('file://', path)
        else:
            # relative path
            url = urlparse.urljoin('file://', abspath(path))
        logger.debug("fixed url = %s", url)
    return url


def is_file_url(url):
    u = urlparse.urlsplit(url)
    return not u.scheme or u.scheme == 'file'


def encode(url, mimetypes):
    """
    Read file with given url and return content. If mimetype of file is binary then encode content with base64.

    If url is not a file:// url return url itself.

    :return: encoded content string or URL or None
    """
    encoded = None
    u = urlparse.urlsplit(url)
    if not u.scheme or u.scheme == 'file':
        with open(u.path, 'r') as fp:
            content = fp.read()
            # TODO: check all mimetypes ... use also python-magic to detect mime type
            if len(mimetypes) == 0 or mimetypes[0].lower() == 'application/xml'\
               or mimetypes[0].lower().startswith('text/'):
                logger.debug('send content of %s', url)
                # TODO: need to fix owslib unicode and complex data type handling
                encoded = str(content.decode('ascii', errors='ignore'))
            else:
                logger.debug('base64 encode content of %s', url)
                encoded = base64.b64encode(content)
    else:
        # remote urls as reference
        logger.debug('send url %s', url)
        encoded = url
    return encoded
