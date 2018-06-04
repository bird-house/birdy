import click
from birdy.cli.base import BirdyCLI

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(cls=BirdyCLI, context_settings=CONTEXT_SETTINGS,
               url="http://localhost:5000/wps")
@click.version_option()
@click.option('--insecure', '-k', is_flag=True, help="Don't validate the server's certificate.")
@click.option('--cert', help="Client side certificate containing both certificate and private key.")
@click.option("--sync", '-s', is_flag=True, help="Execute process in sync mode. Default: async mode.")
@click.option("--token", "-t", help="Token to access the WPS service.")
@click.pass_context
def cli(ctx, insecure, cert, sync, token):
    """
    Birdy is a command line client for Web Processing Services.

    Documentation is available on readthedocs:
    http://birdy.readthedocs.org/en/latest/
    """
    ctx.obj = dict(insecure=insecure, cert=cert, sync=sync, token=token)
