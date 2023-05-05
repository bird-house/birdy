# noqa: D100

import os
from collections import OrderedDict

import click
from jinja2 import Environment, PackageLoader
from owslib.wps import WebProcessingService
from requests.exceptions import SSLError

from birdy.cli.misc import get_ssl_verify
from birdy.cli.types import COMPLEX
from birdy.exceptions import ConnectionError

template_env = Environment(
    loader=PackageLoader("birdy", "templates"),
    autoescape=True,
)


class BirdyCLI(click.MultiCommand):
    """BirdyCLI is an implementation of :class:`click.MultiCommand`.

    Adds each process of a Web Processing Service as command to the command-line interface.

    Parameters
    ----------
    url: str
      URL of the Web Processing Service.
    caps_xml: str
      A WPS GetCapabilities response for testing.
    desc_xml: str
      A WPS DescribeProcess response with "identifier=all" for testing.
    """

    def __init__(self, name=None, url=None, caps_xml=None, desc_xml=None, **attrs):
        click.MultiCommand.__init__(self, name, **attrs)
        self.url = os.environ.get("WPS_SERVICE") or url
        self.verify = get_ssl_verify()
        self.caps_xml = caps_xml
        self.desc_xml = desc_xml
        self._wps = None
        self.commands = OrderedDict()

    @property
    def wps(self):  # noqa: D102
        if self._wps is None:
            language = self.context_settings["obj"].get("language")
            self._wps = WebProcessingService(
                self.url, verify=self.verify, skip_caps=True, language=language
            )
        return self._wps

    def _update_commands(self):  # noqa: D102
        if not self.commands:
            try:
                self.wps.getcapabilities(xml=self.caps_xml)
            except SSLError:
                raise ConnectionError(
                    "SSL verfication of server certificate failed. Set WPS_SSL_VERIFY=false."
                )
            except Exception as e:
                raise ConnectionError(
                    f"Could not connect to Web Processing Service ({e!r})"
                )
            for process in self.wps.processes:
                self.commands[process.identifier] = dict(
                    name=process.identifier,
                    url=self.wps.url,
                    version=process.processVersion,
                    help=BirdyCLI.format_command_help(process),
                    options=[],
                )

    def list_commands(self, ctx):  # noqa: D102
        self._update_commands()
        return list(self.commands.keys())

    def get_command(self, ctx, name):  # noqa: D102
        self._update_commands()
        cmd_templ = template_env.get_template("cmd.py.j2")
        rendered_cmd = cmd_templ.render(self._get_command_info(name, ctx))
        ns = {}
        code = compile(rendered_cmd, filename="<string>", mode="exec")
        eval(code, ns, ns)
        return ns["cli"]

    def _get_command_info(self, name, ctx):  # noqa: D102
        cmd = self.commands.get(name)
        pp = self.wps.describeprocess(name, xml=self.desc_xml)
        for inp in pp.dataInputs:
            help = inp.title or ""
            default = BirdyCLI.get_param_default(inp)
            if default:
                help = f"{help}. Default: {default}"
            cmd["options"].append(
                dict(
                    name=inp.identifier.replace(" ", "-"),
                    # default=BirdyCLI.get_param_default(inp),
                    help=help,
                    type=BirdyCLI.get_param_type(inp),
                    multiple=inp.maxOccurs > 1,
                )
            )
        outputs = []
        for output in pp.processOutputs:
            outputs.append(
                (output.identifier, BirdyCLI.get_param_type(output) is COMPLEX)
            )
        return cmd

    @staticmethod
    def format_command_help(process):  # noqa: D102
        return "{}: {}".format(
            process.title or process.identifier, process.abstract or ""
        )

    @staticmethod
    def get_param_default(param):  # noqa: D102
        if "ComplexData" in param.dataType:
            # TODO: get default value of complex type
            default = None
        elif "BoundingBoxData" in param.dataType:
            # TODO: get default value of bbox
            default = None
        else:
            default = getattr(param, "defaultValue", None)
        return default

    @staticmethod
    def get_param_type(param):  # noqa: D102
        if param.dataType is None:
            param_type = click.STRING
        elif "boolean" in param.dataType:
            param_type = click.BOOL
        elif "integer" in param.dataType:
            param_type = click.INT
        elif "float" in param.dataType:
            param_type = click.FLOAT
        elif "ComplexData" in param.dataType:
            param_type = COMPLEX
        else:
            param_type = click.STRING
        return param_type
