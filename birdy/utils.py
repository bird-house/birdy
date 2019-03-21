import re
import collections
import base64
import six
from six.moves.urllib.parse import urlparse
from pathlib import Path


# These mimetypes will be encoded in base64 when embedded in requests.
# I'm sure there is a more elegant solution than this... https://pypi.org/project/binaryornot/ ?
BINARY_MIMETYPES = ["application/vnd.geo+json",
                    "application/x-zipped-shp",
                    "application/vnd.google-earth.kmz",
                    "image/tiff; subtype=geotiff",
                    "application/x-netcdf",
                    "application/octet-stream",
                    "application/zip",
                    "application/octet-stream",
                    "application/x-gzip",
                    "application/x-gtar",
                    "application/x-tgz",
                    ]

XML_MIMETYPES = ["application/xml", "application/gml+xml", "text/xml"]

DEFAULT_ENCODING = 'utf-8'


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


def is_file(path):
    """Return True if `path` is a valid file."""
    if not path:
        ok = False
    elif isinstance(path, Path):
        p = path
    else:
        p = Path(path[:255])
    try:
        ok = p.is_file()
    except Exception:
        ok = False
    return ok


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


def embed(value, mimetype=None, encoding=None):
    """Return the content of the file, either as a string or base64 bytes.

    :return: encoded content string and actual encoding
    """

    if hasattr(value, 'read'):  # File-like, we don't know if it's open in bytes or string.
        content = value.read()

    else:
        if isinstance(value, Path):
            path = str(value)

        else:
            u = urlparse(value)
            path = u.path

        if is_file(path):
            mode = 'rb' if mimetype in BINARY_MIMETYPES else 'r'
            with open(path, mode) as fp:
                content = fp.read()
        else:
            content = value

    return _encode(content, mimetype, encoding)


def _encode(content, mimetype, encoding):
    """Encode in base64 if mimetype is a binary type."""

    if mimetype in BINARY_MIMETYPES:
        # An error here might be due to a bad file path. Check that the file exists.
        return base64.b64encode(content), 'base64'

    else:
        if encoding is None:
            encoding = DEFAULT_ENCODING

        if isinstance(content, bytes):
            return content.decode(encoding), encoding
        else:
            return content, encoding
        # Do we need to escape content that is not HTML safe ?
        # return u'<![CDATA[{}]]>'.format(content)
