import click
from owslib.wps import WebProcessingService
from six.moves.urllib.parse import quote

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--supported', is_flag=True, help='Returns languages supported by service')
@click.option('--set', help='Set active language for wps service')
@click.pass_context
def cli(ctx, supported, set=None):
    """
    Language parameter for the wps service : Returns the service's current language.
    """

    headers = {}

    if 'token' in ctx.obj:
        headers = {'Authorization': 'Bearer {}'.format(ctx.obj['token'])}
    verify = ctx.obj.get('verify', True)
    cert = ctx.obj.get('cert')
    send = ctx.obj.get('send', False)

    if send and cert:
        with open(cert, 'r') as fh:
            headers = {'X-Ssl-Client-Cert': quote(fh.read())}

    wps = WebProcessingService('{{ url }}', skip_caps=True, verify=verify, cert=cert, headers=headers)

    # TODO Add try:except for set language in case of unsupported language
    try:
        command_output = "Active language : {}".format(wps.language)

        if supported:
            languages = ', '.join(wps.languages)
            command_output = "This wps service supports the following languages : {}".format(languages)
        if set:
            wps.language = set
            command_output = "Changed active language to : {}".format(wps.language)

        click.echo(command_output)

    except AttributeError:
        click.echo("The wps service does not support the language parameter")
