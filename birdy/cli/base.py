import os
import click
from requests.exceptions import SSLError
from jinja2 import Environment, PackageLoader
from owslib.wps import WebProcessingService
from collections import OrderedDict
from birdy.exceptions import ConnectionError
from birdy.cli.types import COMPLEX
from birdy.cli.misc import get_ssl_verify


template_env = Environment(
    loader=PackageLoader('birdy', 'templates'),
    autoescape=True,
)


class BirdyCLI(click.MultiCommand):
    """BirdyCLI is an implementation of :class:`click.MultiCommand`. It
    adds each process of a Web Processing Service as command to the
    command-line interface.

    :param url: URL of the Web Processing Service.
    :param xml: A WPS GetCapabilities response for testing.
    """
    def __init__(self, name=None, url=None, xml=None, **attrs):
        click.MultiCommand.__init__(self, name, **attrs)
        self.url = os.environ.get('WPS_SERVICE') or url
        self.verify = get_ssl_verify()
        self.xml = xml
        self.wps = WebProcessingService(self.url, verify=self.verify, skip_caps=True)
        self.commands = OrderedDict()

    def _update_commands(self):
        if not self.commands:
            try:
                self.wps.getcapabilities(xml=self.xml)
            except SSLError:
                raise ConnectionError('SSL verfication of server certificate failed. Set WPS_SSL_VERIFY=false.')
            except Exception:
                raise ConnectionError("Web Processing Service not available.")
            for process in self.wps.processes:
                self.commands[process.identifier] = dict(
                    name=process.identifier,
                    url=self.wps.url,
                    version=process.processVersion,
                    help=BirdyCLI.format_command_help(process),
                    options=[])

    def list_commands(self, ctx):
        ctx.obj = True
        self._update_commands()
        return self.commands.keys()

    def get_command(self, ctx, name):
        self._update_commands()
        cmd_templ = template_env.get_template('cmd.py.j2')
        rendered_cmd = cmd_templ.render(self._get_command_info(name, details=ctx.obj is None or False))
        ns = {}
        code = compile(rendered_cmd, filename='<string>', mode='exec')
        eval(code, ns, ns)
        return ns['cli']

    def _get_command_info(self, name, details=False):
        cmd = self.commands.get(name)
        if details:
            pp = self.wps.describeprocess(name)
            for inp in pp.dataInputs:
                help = inp.title or ''
                default = BirdyCLI.get_param_default(inp)
                if default:
                    help = "{}. Default: {}".format(help, default)
                cmd['options'].append(dict(
                    name=inp.identifier,
                    # default=BirdyCLI.get_param_default(inp),
                    help=help,
                    type=BirdyCLI.get_param_type(inp),
                    multiple=inp.maxOccurs > 1))
        return cmd

    @staticmethod
    def format_command_help(process):
        return "{}: {}".format(process.title or process.identifier, process.abstract or '')

    @staticmethod
    def get_param_default(param):
        if 'ComplexData' in param.dataType:
            # TODO: get default value of complex type
            default = None
        elif 'BoundingBoxData' in param.dataType:
            # TODO: get default value of bbox
            default = None
        else:
            default = getattr(param, 'defaultValue', None)
        return default

    @staticmethod
    def get_param_type(param):
        if param.dataType is None:
            param_type = click.STRING
        elif 'boolean' in param.dataType:
            param_type = click.BOOL
        elif 'integer' in param.dataType:
            param_type = click.INT
        elif 'float' in param.dataType:
            param_type = click.FLOAT
        elif 'ComplexData' in param.dataType:
            param_type = COMPLEX
        else:
            param_type = click.STRING
        return param_type
