import click
from birdy.cli.base import BirdyCLI
from birdy.cli.misc import get_ssl_verify

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(cls=BirdyCLI, context_settings=CONTEXT_SETTINGS,
               url="http://localhost:5000/wps")
@click.version_option()
@click.option('--cert', help="Client side certificate containing both certificate and private key.")
@click.option('--send', '-S', is_flag=True, help="Send client side certificate to WPS. Default: false")
@click.option("--sync", '-s', is_flag=True, help="Execute process in sync mode. Default: async mode.")
@click.option("--token", "-t", help="Token to access the WPS service.")
@click.pass_context
def cli(ctx, cert, send, sync, token):
    """
    Birdy is a command line client for Web Processing Services.

    Documentation is available on readthedocs:
    http://birdy.readthedocs.org/en/latest/
    """
    ctx.obj = dict(verify=get_ssl_verify(), cert=cert, send=send, sync=sync, token=token)
