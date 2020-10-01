import os

import click
from birdy.cli.base import BirdyCLI
from birdy.cli.misc import get_ssl_verify

from owslib.wps import WebProcessingService

CONTEXT_OBJ = dict(language=None)
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], obj=CONTEXT_OBJ)
DEFAULT_URL = "http://localhost:5000/wps"


def _show_languages(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    url = os.environ.get('WPS_SERVICE') or DEFAULT_URL
    wps = WebProcessingService(url, verify=get_ssl_verify())
    click.echo(','.join(wps.languages.supported))
    ctx.exit()


def _set_language(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    CONTEXT_OBJ['language'] = value


def _format_outputs(ctx, param, output_obj):
    if output_obj:
        output = output_obj[0]
        ref = output_obj[1].lower()
        mime = output_obj[2]
        as_ref = None
        if ref == "true":
            as_ref = True
        elif ref == "false":
            as_ref = False
        mimetype = mime if mime.lower() != "none" else None
        formatted_output = [(output, as_ref, mimetype)]
        print(formatted_output)
        CONTEXT_OBJ['outputs'] = formatted_output


@click.command(cls=BirdyCLI, context_settings=CONTEXT_SETTINGS,
               url="http://localhost:5000/wps")
@click.version_option()
@click.option('--cert', help="Client side certificate containing both certificate and private key.")
@click.option('--outputs', expose_value=False, nargs=3, callback=_format_outputs,
                           help="Modify output format (optional). Takes three arguments, output name, "
                                "as_reference (True, False, or None for process default), and mimetype"
                                "(None for process default).")
@click.option('--send', '-S', is_flag=True, help="Send client side certificate to WPS. Default: false")
@click.option("--sync", '-s', is_flag=True, help="Execute process in sync mode. Default: async mode.")
@click.option("--token", "-t", help="Token to access the WPS service.")
@click.option(
    "--language", "-l", expose_value=False, is_eager=True, callback=_set_language,
    help="Set the accepted language to send to the WPS service.")
@click.option(
    "--show-languages", "-L", expose_value=False, is_flag=True, is_eager=True, callback=_show_languages,
    help="Show a list of accepted languages for the WPS service.")
@click.pass_context
def cli(ctx, cert, send, sync, token):
    """
    Birdy is a command line client for Web Processing Services.

    Documentation is available on readthedocs:
    http://birdy.readthedocs.org/en/latest/
    """
    ctx.obj = ctx.obj or dict()
    ctx.obj['verify'] = get_ssl_verify()
    ctx.obj['cert'] = cert
    ctx.obj['send'] = send
    ctx.obj['sync'] = sync
    ctx.obj['token'] = token
