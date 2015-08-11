import urlparse
from os.path import curdir, abspath, join

import logging
logger = logging.getLogger(__name__)

def fix_local_url(url):
    u = urlparse.urlsplit(url)
    if not u.scheme:
        # build local file url
        if u.path.startswith('/'):
            # absolute path
            url = urlparse.urljoin('file://', u.path)
        else:
            # relative path
            url = urlparse.urljoin('file://', abspath(join(curdir, u.path)))
        logger.debug("fixed url = %s", url)
    return url
