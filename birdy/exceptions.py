# noqa: D100

import click
from owslib.util import ServiceException


class ConnectionError(click.ClickException):  # noqa: D101
    pass


class UnauthorizedException(ServiceException):  # noqa: D101
    pass


class IPythonWarning(UserWarning):  # noqa: D101
    pass


class ProcessIsNotComplete(Exception):  # noqa: D101
    pass


class ProcessFailed(Exception):  # noqa: D101
    pass


class ProcessCanceled(Exception):  # noqa: D101
    pass
