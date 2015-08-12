import urlparse
from os.path import curdir, abspath, join

import logging
logger = logging.getLogger(__name__)

def fix_local_url(url):
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
