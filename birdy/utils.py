import re
import collections

import six
from six.moves.urllib.parse import urlparse


def is_url(url):
    if url is None:
        return False
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        return False
    else:
        return True


def sanitize(name):
    """Lower-case name and replace all non-ascii chars by `_`."""
    return re.sub(r'\W|^(?=\d)', '_', name.lower())


def delist(data):
    """If data is a sequence with a single element, returns this element, otherwise return the sequence."""
    if (
        isinstance(data, collections.Iterable) and not isinstance(data, six.string_types) and len(data) == 1
    ):
        return data[0]
    return data
