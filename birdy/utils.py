from six.moves.urllib.parse import urlparse


def is_url(url):
    if url is None:
        return False
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        return False
    else:
        return True
