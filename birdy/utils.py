import re
import collections
import base64
import six
from six.moves.urllib.parse import urlparse, urljoin
from pathlib import Path


# These mimetypes will be encoded in base64 when embedded in requests.
BINARY_MIMETYPES = ["application/vnd.geo+json", "application/x-zipped-shp", "application/vnd.google-earth.kmz",
                    "image/tiff; subtype=geotiff", "application/x-netcdf", "application/octet-stream"]


def fix_url(url):
    """If url is a local path, add a file:// scheme."""
    return urlparse(url, scheme='file').geturl()


def is_url(url):
    """Return whether value is a valid URL."""
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


def encode(value, mimetype=None):
    """Return the content of the file, either as a string or base64 bytes.

    :return: encoded content string
    """

    if hasattr(value, 'read'):  # File-like
        content = value.read()

    else:
        if isinstance(value, Path):
            path = str(value)

        else:
            u = urlparse(value)
            path = u.path

        if Path(path).is_file():
            mode = 'rb' if mimetype in BINARY_MIMETYPES else 'r'
            with open(path, mode) as fp:
                content = fp.read()
        else:
            content = value

    return _encode(content, mimetype)


def _encode(content, mimetype):
    """Encode in base64 if mimetype is a binary type."""
    if mimetype not in BINARY_MIMETYPES:
        return str(content)
    else:
        return base64.b64encode(content)
