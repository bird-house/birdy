import click
from owslib.util import ServiceException


class ConnectionError(click.ClickException):
    pass


class UnauthorizedException(ServiceException):
    pass


class IPythonWarning(UserWarning):
    pass
