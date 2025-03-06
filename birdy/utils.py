import base64
import collections
import keyword
import re
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import urlparse

# These mimetypes will be encoded in base64 when embedded in requests.
# I'm sure there is a more elegant solution than this... https://pypi.org/project/binaryornot/ ?
BINARY_MIMETYPES = [
    "application/x-zipped-shp",
    "application/vnd.google-earth.kmz",
    "image/tiff; subtype=geotiff",
    "image/tiff; application=geotiff",
    "application/x-netcdf",
    "application/octet-stream",
    "application/zip",
    "application/x-gzip",
    "application/x-gtar",
    "application/x-tgz",
]

XML_MIMETYPES = ["application/xml", "application/gml+xml", "text/xml"]

DEFAULT_ENCODING = "utf-8"


def fix_url(url: str) -> str:
    """
    If url is a local path, add a file:// scheme.

    Parameters
    ----------
    url : str
        URL or local path.

    Returns
    -------
    str
        URL with a file:// scheme.
    """
    return urlparse(url, scheme="file").geturl()


def is_url(url: Optional[str]) -> bool:
    """
    Return whether value is a valid URL.

    Parameters
    ----------
    url : str
        URL or local path.

    Returns
    -------
    bool
        True if value is a valid URL.
    """
    if url is None:
        return False
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        return False
    else:
        return True


def is_opendap_url(url: str) -> bool:
    """
    Check if a provided url is an OpenDAP url.

    The DAP Standard specifies that a specific tag must be included in the
    Content-Description header of every request. This tag is one of:
    "dods-dds" | "dods-das" | "dods-data" | "dods-error"

    So we can check if the header starts with `dods`.

    Parameters
    ----------
    url : str
        URL.

    Returns
    -------
    bool
        True if the URL is an OpenDAP URL.

    Notes
    -----
    This might not work with every DAP server implementation.
    """
    import requests
    from requests.exceptions import ConnectionError, InvalidSchema, MissingSchema

    try:
        content_description = requests.head(url, timeout=5).headers.get(
            "Content-Description"
        )
    except (ConnectionError, MissingSchema, InvalidSchema):
        return False

    if content_description:
        return content_description.lower().startswith("dods")
    else:
        return False


def is_file(path: Optional[str]) -> bool:
    """
    Return True if `path` is a valid file.

    Parameters
    ----------
    path : str or Path
        Path to a file.

    Returns
    -------
    bool
        True if `path` is a valid file.
    """
    if not path:
        return False
    elif isinstance(path, Path):
        p = path
    else:
        p = Path(path[:255])
    try:
        ok = p.is_file()
    except (OSError, ValueError):
        ok = False
    return ok


def sanitize(name: str) -> str:
    """
    Lower-case name and replace all non-ascii chars by `_`.

    If name is a Python keyword (like `return`) then add a trailing `_`.

    Parameters
    ----------
    name : str
        Name to sanitize.

    Returns
    -------
    str
        Sanitized name.
    """
    new_name = re.sub(r"\W|^(?=\d)", "_", name.lower())
    if keyword.iskeyword(new_name):
        new_name = new_name + "_"
    return new_name


def delist(data: Any) -> Any:
    """
    If data is a sequence with a single element, returns this element, otherwise return the sequence.

    Parameters
    ----------
    data : Any
        Data to check.

    Returns
    -------
    Any
        Single element or sequence.
    """
    if (
        isinstance(data, collections.abc.Iterable)
        and not isinstance(data, str)
        and len(data) == 1
    ):
        return data[0]
    return data


def embed(
    value: Any, mimetype: Optional[str] = None, encoding: Optional[str] = None
) -> Union[tuple[bytes, str], tuple[str, Union[str, Any]], tuple[Any, Union[str, Any]]]:
    """
    Return the content of the file, either as a string or base64 bytes.

    Parameters
    ----------
    value : Any
        File path, URL, or file-like object.
    mimetype : str, optional
        Mimetype of the file.
    encoding : str, optional
        Encoding of the file.

    Returns
    -------
    tuple
        Encoded content string and actual encoding.
    """
    if hasattr(
        value, "read"
    ):  # File-like, we don't know if it's open in bytes or string.
        content = value.read()

    else:
        if isinstance(value, Path):
            path = str(value)

        else:
            u = urlparse(value)
            path = u.path

        if is_file(path):
            mode = "rb" if mimetype in BINARY_MIMETYPES else "r"
            with open(path, mode) as fp:
                content = fp.read()
        else:
            content = value

    return _encode(content, mimetype, encoding)


def _encode(content, mimetype, encoding):
    """Encode in base64 if mimetype is a binary type."""
    if mimetype in BINARY_MIMETYPES:
        # An error here might be due to a bad file path. Check that the file exists.
        return base64.b64encode(content), "base64"

    else:
        if encoding is None:
            encoding = DEFAULT_ENCODING

        if isinstance(content, bytes):
            return content.decode(encoding), encoding
        else:
            return content, encoding
        # Do we need to escape content that is not HTML safe ?
        # return u'<![CDATA[{}]]>'.format(content)


def guess_type(
    url: Union[str, Path], supported: Union[list[str], tuple[str]]
) -> tuple[str, str]:
    """
    Guess the mime type of the file link.

    If the mimetype is not recognized, default to the first supported value.

    Parameters
    ----------
    url : str or Path
        A path or URL to a file.
    supported : list or tuple
        Supported mimetypes.

    Returns
    -------
    tuple
        Mimetype and encoding.
    """
    import mimetypes

    try:
        mime, enc = mimetypes.guess_type(str(url), strict=False)
    except TypeError:
        mime, enc = None, None

    # Special cases
    # -------------

    # netCDF
    if (
        mime == "application/x-netcdf"
        and "dodsC" in str(url)
        and "application/x-ogc-dods" in supported
    ):
        mime = "application/x-ogc-dods"

    # ZIP
    zips = ["application/zip", "application/x-zipped-shp"]
    if mime not in supported:
        if mime in zips and set(zips).intersection(supported):
            mime = set(zips).intersection(supported).pop()

    # GeoJSON
    if mime == "application/json" and "application/geo+json" in supported:
        mime = "application/geo+json"

    # FIXME: Verify whether this code is needed. Remove if not.
    # # GeoTIFF (workaround since this mimetype isn't correctly understood)
    # if mime == "image/tiff" and (".tif" in url or ".tiff" in "url"):
    #     mime = "image/tiff; subtype=geotiff"
    #

    # All the various XML schemes
    # TODO

    # If unrecognized, default to the first supported mimetype
    if mime is None:
        mime = supported[0]
    else:
        if mime not in supported:
            raise ValueError(f"mimetype {mime} not in supported mimetypes {supported}.")

    return mime, enc
